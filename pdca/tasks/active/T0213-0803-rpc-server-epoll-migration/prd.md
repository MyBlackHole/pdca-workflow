# rpc-server → rpc-epoll 调度层迁移 — 规格文档（T0213）

## 问题陈述

- **现状**: rpc-server 使用 thread-per-conn 模型：`RPCServiceThread`（rpc-server.cpp:68-153）
  accept 循环，`RPCService`（L155-175）每连接 `create_thread(StartRPCServiceWoker)` 一个
  detached 线程（libs/thread.c:20，无池、无上限、不 join）；keepalive 依赖内核
  SO_KEEPALIVE（accept 线程 L137-140，2h 级盲区）；T0211 已交付的 rpc-epoll 调度层
  （单 Reactor + 有界 worker 池 + 有界队列 = max_conn + 应用层 Ping/Pong 心跳）目前
  **零集成**：rpc-server.cpp 无引用、aio-speedd 未链接 rpc-epoll.cpp、rpc-config 无
  max_conn/max_workers/queue_capacity 字段，唯一使用方是测试 conn_limit.cpp。
- **目标**: TCP 主服务（端口 g_rpc_config->rpc_port，默认 6611）由 rpc-epoll 调度层接管：
  单 Reactor 收 accept/可读事件，有界 worker 池处理，连接上限 max_conn（超限拒绝）、
  队列满回 `RPC_ERR_QUEUE_FULL`、应用层心跳替代 SO_KEEPALIVE；业务分发链
  （SCP 上传/下载、file_stat、TLS 握手等）行为与消息语义完全不变。
- **差距**: thread-per-conn 无连接上限与背压，资源不可控；keepalive 存在 2h 盲区；
  调度逻辑（T0211 交付）与业务逻辑（rpc-server）双轨并存，生产路径未接入
  ADR-0011 定义的模型。

## 解决方案

- main.cpp 服务启动路径改调 `rpc_epoll_new`/`rpc_epoll_start`（port = rpc_port，
  handler = 新增适配包装），移除 `RPCServiceThread`/`RPCService` 的 accept 与
  thread-per-conn 分派。
- 新增 `rpc_conn_handler` 适配层（签名 `int (int connfd, void *ctx)`）：
  - 按连接管理业务上下文（woker_info 形态：connfd/user/serv/host/net_buf/
    resp_net_buf/流缓冲），首次事件分配、连接终结（handler 返回非 0）释放；
  - `StartRPCServiceWoker` 主体改造为**单次请求处理**（ADR-0011 L31）：读一帧 →
    分发 → 响应 → 返回 0 交还 Reactor 重新挂 EPOLLONESHOT；SCP 流式请求
    （上传 INIT/DATA×N/END、下载 push 帧序列）作为一个逻辑请求在单次
    handler 调用内完成；
  - TLS 握手在首次 handler 调用执行（原 L198-211 语义保留）。
- rpc-config 扩展 `max_conn`/`max_workers`/`queue_capacity`/`keepalive_interval`
  字段与 ini 解析，构造 `struct rpc_epoll_config` 传给 rpc_epoll_new。
- SO_KEEPALIVE 移除（accept 线程消失），空闲保活由 rpc-epoll 应用层
  Ping/Pong（heartbeat_tick）接管，keepalive_interval 来自配置。
- rpc/xmake.lua：aio-speedd target 加入 rpc-epoll.cpp。
- Unix socket 服务（start_unix_server）**不迁移**，保持现状。
- 新增集成测试：真实业务 handler + rpc_epoll_start 驱动，覆盖端到端
  SCP 上传/下载、多请求长连接复用、max_conn 超限、队列满、心跳断连。

## Seam 分析

### 测试接缝
- 集成层（新）：rpc-epoll 启动真实业务 handler，测试客户端连真实监听端口 —
  端到端覆盖迁移语义；与 conn_limit.cpp（纯调度层）互补。
- 业务层（既有）：scp_stream.cpp 已直调 OnMsgScpUpload/rpc_scp_download —
  迁移后其调用签名不变（分发函数保持 woker_info 入口），继续有效。
- 帧协议层（既有）：heart_beat/protocol_roundtrip/frame_validation 不受影响。
- Mock/Stub 策略：不 mock 网络与业务；用真实 socketpair/监听端口；超时类
  用例用短 keepalive_interval 配置驱动。

### 验收可测性
- 每个 AC 有明确 pass/fail 信号（见验收标准）。
- 超限拒绝/队列满/心跳断连均可在测试内构造（小 max_conn/queue/interval）。
- 全量回归 xmake test 防既有 target 回归。

## 用户故事

1. 作为服务管理员，我想要配置连接上限 max_conn，以便在异常客户端下保护服务资源
   —— 超限连接被拒绝并收到错误帧。
2. 作为客户端，我想要长时间空闲连接不被内核 2h 盲区拖死，以便可靠保活
   —— 应用层 Ping/Pong 心跳接管，死连接被判定断开。
3. 作为并发客户端群，我想要服务在负载下可控排队，以便背压而不是无限建线程
   —— 有界 worker 池 + 队列满 RPC_ERR_QUEUE_FULL。
4. 作为既有 SCP 用户，我想要迁移后上传/下载行为完全不变，以便平滑升级。

## 实现决策

- **模块**：rpc-server.cpp（调度路径替换 + 单次请求处理改造）、rpc-config.h/.cpp
  （4 字段扩展）、main.cpp（启动改道 rpc_epoll_start）、rpc/xmake.lua
  （aio-speedd 链接）、rpc/tests/（新增集成测试）。
- **handler 适配层**：`int rpc_epoll_conn_handler(int connfd, void *ctx)`；
  业务上下文按连接分配，终结即释放；上下文持有既有分发所需状态
  （net_buf 等大缓冲，避免栈上 2MB）。
- **单次请求语义**：handler 每次调用处理一个逻辑请求；流式请求整体完成；
  处理完成后返回 0 由 Reactor 重新挂载。
- **心跳职责**：SO_KEEPALIVE 不再设置；rpc-epoll heartbeat_tick 为唯一保活源。
- **配置契约**：rpc_epoll_config{max_conn, max_workers, queue_capacity,
  keepalive_interval} 全部来自 rpc-config ini 解析；缺省值由实现决定并写入文档。
- **不迁移**：Unix socket 服务、TLS 证书逻辑（仅移入 handler 首次调用）、
  消息分发 if-else 链（保持原样，仅改调用方式）。

## 验收标准

- [ ] AC-1: 服务端启动经 rpc-epoll：main 路径调 rpc_epoll_start，`RPCServiceThread`
      accept/thread-per-conn 分派代码移除（无 create_thread(StartRPCServiceWoker) 调用）
- [ ] AC-2: SCP 上传端到端：经真实监听端口 + 业务 handler，64MB 文件 sha256 一致
- [ ] AC-3: SCP 下载端到端：经真实监听端口，文件内容与元数据（mode/atim/mtim）保持
- [ ] AC-4: 多请求长连接复用：同一连接连续 N 个请求（含至少一个 SCP 流式请求）
      全部成功，连接归还 Reactor 语义正确
- [ ] AC-5: max_conn 生效：配置 max_conn=2，第 3 连接被拒（真实服务路径）
- [ ] AC-6: 队列满：worker 全忙 + 队列满，新事件连接收到 RPC_ERR_QUEUE_FULL 后关闭
- [ ] AC-7: 心跳：keepalive_interval 配置生效，空闲连接 Ping/Pong 维持，
      无响应连接在 2×interval 内被判定断开
- [ ] AC-8: rpc-config 解析 max_conn/max_workers/queue_capacity/keepalive_interval
      并传入 rpc_epoll_config（ini 缺省值与显式值均有测试）
- [ ] AC-9: aio-speedd 链接 rpc-epoll.cpp，xmake 构建通过
- [ ] AC-10: 旧 thread-per-conn 路径无残留：grep RPCServiceThread/StartRPCServiceWoker
      直接调用链 0 残留（handler 内改造后的单次请求函数除外）
- [ ] AC-11: 全量回归：xmake test 全部 target 通过（T0211/T0212 相关不回归）

## 范围外

- Unix socket 服务迁移
- 消息分发 if-else 链重构（消息表/注册器）
- rpc-epoll 本身语义修改（EPOLLONESHOT、tick 改动态 deadline 等，见 ADR-0011
  偏差记录，另行处理）
- 客户端（rpc-command/rpc.cpp）任何改动

## 备注

- ADR-0011 已确认；本任务将其 L31 重构方向落地。
- 已知偏差记录：rpc-epoll 实现 epoll_wait 为固定 100ms tick（非动态 deadline）、
  "默认 8/CPU 核数"仅为注释（rpc_epoll_new 对非法 cfg 返回 NULL）——迁移时
  显式传值，不依赖默认。
