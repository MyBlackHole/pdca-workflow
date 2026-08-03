# rpc 协议层与传输层重构 — 规格文档（对齐工业实现）

## 问题陈述

- **现状**: rpc 协议层（rpc-protocol.h/cpp 1453 行 + rpc-metadata.c 928 行）手写 hton/ntoh 序列化样板，无协议魔数/版本/长度上限；服务端为 thread-per-connection（无限）+ 阻塞 IO + poll 单 fd 超时，无连接上限、无线程池、无统一超时管理；传输层 readn/writev 部分读写不处理；命名混乱（`mmsg_ioctl_fsbackup_resp__`、`bolck_num`）；`unsigned long rate` 32/64 位平台不一致；`header` 与 payload 整体加解密（违反业界"header 永不加密"）。
- **目标**: 对齐工业 RPC 实现——16 字节帧头协议演进、C/C++ 分层（序列化层保持 C、传输/调度层 C++）、服务端 epoll 事件循环 + 有界工作线程池 + 连接上限 + 统一超时、客户端同步 API + 内部非阻塞、传输层部分读写/长度上限修复。
- **差距**: 协议无演进能力与防护；服务端资源无界（连接=线程，可被耗尽）；IO 模型落后（无事件循环、无连接管理）；序列化样板 900+ 行。

## 解决方案

### 1. 协议层：16 字节帧头演进（对齐 tRPC 固定帧头）

```
  偏移  字段        说明
  0-3   magic       'FSBC' = 0x46534243，协议识别
  4     version     协议版本 = 1
  5     type        0=请求 1=响应 2=流数据(STREAM) 3=Ping 4=Pong（心跳）
  6-7   flags       bit0=COMPRESSED bit1=ENCRYPTED bit2=END（帧级）
  8-11  total_len   帧总长含帧头 —— 先校验再分配
  12-15 msg_id      请求 ID（当前串行置 0，未来多路复用）
  ```

- 收包校验顺序（业界强制）：读帧头 → 校验 magic → 校验 version → 校验 total_len 上限（8MB，覆盖 4MB 数据块 + 帧头 + 压缩膨胀余量）→ 才分配内存
- **header 永不加密**，仅 payload 加解密（uRPC 实践）；压缩/加密由帧头 flags 帧级独立控制，去掉对连接级协商的依赖
- msg_base（uiMT/uiLEN）**保持不动**：uiLEN 被业务层 159 处直接使用

### 1b. 流式块传输（对齐 gRPC streaming + PBS 4MB chunk）

- 帧头 `type=2 (STREAM)` + flags 流控制位；上传/下载大文件改为流帧序列：
  ```
  INIT(元数据: 文件名/块大小/总大小) → N×DATA(4MB 块) → END
  ```
- **块大小 4MB**（对齐 Proxmox 内容分块）；每块独立 LZ4 压缩 + AES 加密 + CRC 校验（PBS 块级处理模式）
- **块缓冲池化**（freelist/对象池，对应 gRPC `sync.Pool` 实践）：O(4MB) 内存峰值，替代整帧 64MB 缓冲
- **请求级 deadline**（对齐 Seastar timeout propagation）：INIT 帧带 timeout_ms 字段，服务端超时未完成返回超时错误；替代单一连接级 read_timeout 语义
- 单帧上限收紧至 8MB（数据 4MB + 头 + 压缩膨胀余量），128MB 上限作废
- 影响范围：仅 upload/download block 路径（rpc.cpp 上传/下载、rpc-client ScpUpload/ScpDownload、rpc-server OnMsgScpUpload/OnMsgDownloadBlock）；其余小消息处理函数保持整帧不动

### 1c. 心跳与错误码体系（对齐 uRPC Ping/Pong + tRPC 错误模型）

- **应用层心跳**：帧头 `type=3 Ping / type=4 Pong`，空闲连接按 keepalive_interval 周期性 Ping，超时未收到 Pong 判定死连接断开；补充内核 SO_KEEPALIVE（2h）的检测盲区
- **标准化错误码**：枚举 `RPC_ERR_OK=0`、`RPC_ERR_PROTO_VERSION`、`RPC_ERR_FRAME_TOO_LARGE`、`RPC_ERR_BAD_MAGIC`、`RPC_ERR_TIMEOUT`、`RPC_ERR_IO`、`RPC_ERR_PEER_CLOSED` 等，统一返回路径
- **错误详情**：响应/END 帧带错误消息字符串（可读排障信息），替代裸 int uiResult

### 2. 序列化：C/C++ 分层（工业混合常态，uRPC C 序列化 + tRPC C++ IO）

- **序列化层保持 C**（rpc-msg.c、rpc-metadata.c 不改语言，对齐 uRPC 嵌入式风格）：序列化是纯内存操作（hton/ntoh），C 实现与 C++ 无差别；msg_base 本就是 C struct；lz4/crc32 同为 C 库；避免无谓 extern "C" 桥接
- 序列化样板消除：以 `msg_*_hton/ntoh` 为函数签名（rpc-msg.h 保持 C 可包含），内部用**宏生成 + 统一助手函数**压缩样板（对齐 uRPC 宏化序列化方式）
- **传输/调度层用 C++**（rpc-conn/rpc-io/rpc-server 新 epoll 模块）：RAII 管理连接所有权转移（本次重构最大风险点），对齐 tRPC/gRPC/Seastar/muduo
- 统一命名：`mmsg_`→`msg_`、`bolck`→`block`、`decr`→保留但规范化
- 修复 `unsigned long rate` → `uint64_t`（32/64 位平台序列化一致性）
- 不引入 protobuf/flatbuffers/capnproto：单语言、两端同仓库、无跨语言需求、消息体多为文件数据，引入无收益

### 3. 服务端 IO/线程模型：单 Reactor + 工作线程池（对齐 Netty/muduo）

- 主线程 epoll 事件循环（水平触发）：listenfd accept + 连接可读事件 + 统一超时管理（`epoll_wait timeout = 最近 deadline`，不用 timerfd）
- 有界工作线程池（默认 = CPU 核数，rpc-config 可配 `max_workers`），执行请求处理
- **有界任务队列**（容量 = max_conn，对齐 SafeRPC in_flight 限制）：队列满时拒绝新任务（拒绝/关闭对应连接），防止内存膨胀
- **连接数上限**（默认 **8**，rpc-config 可配 `max_conn`）：超限 accept 后立即关闭（防 DoS）；内存预算：8 连接 × ~220MB/连接 ≈ <2GB 峰值
- **连接所有权转移**：worker 处理请求期间独占该连接（事件循环不碰），处理完成归还；避免超时/断开导致的 use-after-free
- **事件循环线程内禁止阻塞操作**（accept 非阻塞、epoll_wait、快速入队）
- 大帧按实际 total_len 分配（不预分配 128MB）
- 每连接请求仍串行（响应顺序语义不变）；不同连接由线程池并行
- 现有处理函数（rpc_scp_download 等 30+ 个）**保持同步式不动**，事件循环只做调度；唯一例外：upload/download 两条路径按流式块消费（见 1b）
- 优雅关闭：连接关闭从 epoll 移除、线程池任务 drain、listen 停止
- 重构位置：`RpcService::RPCServiceThread` 的 while 循环 → 新增调度层；`StartRPCServiceWoker` 改为单次请求处理

### 4. 客户端：同步 API + 内部非阻塞（对齐 SDK 实践）

- 对外 API 签名不变（session/conn 模型），业务层零改动
- 传输层内部：非阻塞 socket + 超时管理 + 部分读写循环修复
- 帧编解码与服务器共用（rpc-msg/帧头）
- scp 并发限流（每文件一线程无上限）属业务层，范围外

### 5. 传输层安全修复

- readn：EAGAIN 继续等待（非阻塞场景），EINTR 重试，返回完整字节数语义
- writev：部分写入循环处理（大消息 + 非阻塞不丢数据）
- 长度上限校验在内存分配前
- RPC_CONN_RETRY 宏保持不动（业务层 backup/restore-client 使用）

### 6. 升级策略

- 两端同步升级（客户端/服务端同仓库）；版本不匹配返回明确错误码（`RPC_ERR_PROTO_VERSION`）并断开
- 不做多版本并存（用户否决；仓库内无外部实现）

## Seam 分析

### 测试接缝
- 协议层：序列化 round-trip（新 test target `tests/protocol_roundtrip.cpp`）
- 传输层：socketpair 直测 rpc_conn 层（现有测试模式），新增部分读写/超限帧测试
- 服务端调度：帧头校验顺序测试（magic 错/版本错/超限帧均拒绝）

### 验收可测性
- 每个验收标准独立 pass/fail（见下）
- 现有 tests/ 全部通过 = 回归基线

## 用户故事

1. 作为 rpc 维护者，我想要协议帧带魔数/版本/长度上限校验，以便安全演进协议且不被恶意帧耗尽内存。
2. 作为 rpc 维护者，我想要服务端有界线程池 + 连接上限，以便连接数/线程数可控，不被耗尽。
3. 作为 rpc 维护者，我想要 epoll 事件循环 + 统一超时，以便连接管理现代化、超时行为一致。
4. 作为 rpc 维护者，我想要序列化层用 C 宏化消除 900+ 行手写样板（uRPC 方式），且不引入 C/C++ 语言边界，以便保持轻量与类型安全平衡。
5. 作为 rpc 维护者，我想要传输层正确处理部分读写，以便大消息不丢数据。
6. 作为 rpc 维护者，我想要帧级压缩/加密 flags，以便帧粒度控制，header 明文可解析。
7. 作为 rpc 维护者，我想要流式块传输（INIT→DATA→END + 4MB 块 + 缓冲池），以便大文件内存峰值从 64MB 降到 4MB 级。
8. 作为 rpc 维护者，我想要请求级 deadline + 心跳 + 错误码体系，以便单请求不挂死、死连接快速发现、错误可读。

## 实现决策

- 修改模块：
  - 新增：`rpc-epoll.h/cpp`（事件循环 + 线程池 + 连接管理，服务端调度层，C++）
  - 修改：rpc-protocol.h/cpp（帧头，C++）、rpc-msg.c（帧编解码 + 长度上限，**保持 C**）、rpc-metadata.c（元数据序列化，**保持 C**）、rpc-conn.cpp/h（帧级 flags + 非阻塞语义，C++）、rpc-io.cpp/h（部分读写修复，C++）、rpc-server.cpp（调度层替换 + 处理函数签名适配，C++）、rpc-config（max_workers/max_conn）、xmake.lua
  - 客户端：rpc-client.cpp 的传输调用点适配（API 不变）
- 对外 API 合约：`rpc_conn_*`、`msg_*_hton/ntoh` 函数签名保持，内部实现替换；帧头在 rpc-msg 层解析
- 架构决策 → docs/adr/
- 数据模型变更：wire 层新增 16 字节帧头；消息结构字段仅重命名
- 压缩/加密：帧头 flags 帧级控制，header 明文

## 测试决策

- 新增 test targets（跟随现有 xmake 测试模式，无 gtest）：
  - `tests/protocol_roundtrip.cpp`：全部消息序列化往返字节级一致
  - `tests/frame_validation.cpp`：magic 错/版本错/超限帧/截断帧均拒绝且不分配大内存
  - `tests/io_partial.cpp`：模拟部分读写/EINTR/EAGAIN 场景
  - `tests/conn_limit.cpp`：服务端连接上限拒绝行为
  - `tests/stream_blocks.cpp`：流帧序列 INIT→DATA→END 完整往返、分块数/校验/内存峰值验证
  - `tests/bench_throughput.cpp`：1GB 流式传输吞吐基准（AC-11）
- 现有 `rpc/tests/*` 全部通过为回归基线
- 测试通过 socketpair 直测 rpc_conn 层（现有模式）

## 验收标准

- [ ] AC-1: 帧头含 magic/version/total_len，magic 错、版本不匹配、超限帧均被拒绝且返回明确错误码
- [ ] AC-2: 接收帧 total_len 超过上限（8MB）时在内存分配前拒绝
- [ ] AC-3: 所有 msg_*_hton/ntoh 序列化往返字节级一致（round-trip 测试通过）
- [ ] AC-4: 传输层在 EINTR/EAGAIN/部分 writev 场景下不丢数据不挂死
- [ ] AC-5: 压缩/加密由帧头 flags 帧级控制，header 明文仅 payload 加解密
- [ ] AC-6: 服务端 epoll 事件循环 + 工作线程池 + 连接上限生效，超限连接被拒绝
- [ ] AC-7: 统一超时管理生效，空闲连接按超时断开
- [ ] AC-8: rpc/tests/ 现有测试全部通过（回归基线）
- [ ] AC-9: 命名统一（mmsg_→msg_、bolck→block），无 sprintf/strcpy 新增
- [ ] AC-10: 客户端对外 API 不变，业务层（rpc.cpp/rpc-client.cpp 业务逻辑）零改动
- [ ] AC-11: 性能回归：流式大文件（如 1GB）上传/下载吞吐对比重构前基准，劣化 <5%
- [ ] AC-12: 流帧序列正确：INIT→DATA→END 完整往返，DATA 分块数正确，END 前帧内数据可校验
- [ ] AC-13: 流式传输内存峰值 ≤ 4MB 数据块级别（无整帧 64MB 缓冲残留）
- [ ] AC-14: 有界任务队列满时拒绝新任务，不无限堆积
- [ ] AC-15: 请求级 deadline 生效：INIT 带超时，服务端超时返回 RPC_ERR_TIMEOUT
- [ ] AC-16: 心跳生效：空闲连接 Ping/Pong 往返正常，无响应连接按超时断开
- [ ] AC-17: 错误码体系：标准化枚举 + 错误详情字符串在响应/END 帧中正确传递

## 范围外

- rpc.cpp/rpc-server.cpp 业务处理逻辑（目录遍历、scp 流程等；upload/download 流式化例外）
- scp 并发限流（业务层，后续任务）
- RPC_CONN_RETRY 宏（业务层使用）
- 多路复用（帧头 msg_id 预留，不启用）
- 多版本协议并存（同步升级策略）
- dir_traversal 等 rpc-common 工具函数
- sendfile/splice 零拷贝（有压缩/加密/校验变换，不适用，工业结论）

## 备注

- 协议两端均在本仓库，可同步升级；aio-speed 是客户端（client_main），随客户端同步
- 序列化层头文件（rpc-msg.h/rpc-metadata.h）保持 C 可包含（extern "C" 供 C++ 调用方）
- 帧头对齐 tRPC 16 字节固定帧头设计（magic/type/total_len/version/reserved 同构）
- 语言分层依据：项目 116 .c + 112 .cpp 混合工程；rpc 模块 22/26 为 C++，仅序列化/算法（crc32/lz4）为 C；uRPC 证明 C 序列化可行，tRPC/Seastar 证明 C++ IO 可行

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
