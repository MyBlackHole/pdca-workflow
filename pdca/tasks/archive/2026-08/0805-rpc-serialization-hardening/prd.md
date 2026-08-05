# T0217 rpc 序列化补强 — 规格文档（定稿）

## 问题陈述

- **现状**: 帧头层已有防护（T0211：magic/version/total_len 上限，先校验后分配）。
  但**消息体层 14 个 `msg_*_ntoh` 变长字段长度直接取自对端并立即 memcpy**
  （rpc-protocol.cpp，如 msg_cmd_ntoh L184、msg_mkdir_ntoh L245），服务端分发仅
  解析 uiMT/uiLEN 未校验 uiLEN ≤ 实际读入 bytes（rpc-server.cpp:170-178），恶意/
  损坏帧可构造超大 len 造成 host_buf 越界读写。字节序方面项目内**并存**：metadata
  层已用 `htole32/le64toh`（小端，rpc-metadata.h），rpc 协议层用 `htonl/ntohll`
  （大端，244 处），misc.c 有 `get_u32_le/put_u32_le` 但 buf 层无 LE 变体。
- **目标**: ① 全部变长字段 ntoh 前做长度上限校验（对齐 knowledge"字段级再校验"）；
  ② 分发层 uiLEN 预检；③ 协议层字节序统一切换为**小端**（对齐备份工业实践
  PBS/restic 与项目已有 metadata 层）。
- **差距**: 安全校验缺失 + 字节序项目内不一致。

## 解决方案

### 1. 消息体就地化解析 + 变长字段上限校验（核心）

- **就地化（用户拍板纳入本次）**：全部 `msg_*_ntoh` 就地化，签名改为
  `int msg_xxx_ntoh(msg_xxx_t *msg, size_t net_len)`，直接在 wire 缓冲
  （net_buf）上就地转换字段 + 校验变长字段边界，返回 0 / RPC_ERR_BAD_FRAME。
- **原理**：小端 wire 字节序 = 小端主机序，net_buf 强转即直接可用（le32toh 小端
  编译期恒等零开销）；ntoh 降级为"就地转换 + 边界校验"，**不再 memcpy 到 host_buf**
  （消除大 payload 如 dir_tree/download_block/upload_block 的整段冗余拷贝）。
  大端主机同样正确（le32toh 自动 bswap），跨字节序安全。
- **校验规则**（T0217 原安全目标，就地化顺带实现）：
  - `net_len >= sizeof(msg_t)`（固定头下限，杜绝截断帧越界读）；
  - 变长字段（cmd_len/path_len/name_len/key_len/data_len 等）就地转换后校验
    `len <= net_len - offsetof(变长字段起始)`；
  - 定长数组（如 data[512]）另校验 `len <= 数组容量`；
  - 既有一处兜底（execute_cmd L697 MIN 截断）保留，不依赖其兜底。
- 服务端分发层（rpc-server.cpp:170-178）rpc_recv 后就地解析 msg_base（uiMT/uiLEN）
  并校验 `uiLEN <= 实际读入 bytes`，不符拒绝连接。
- **接收长度传递**：woker_info 新增 `msg_len` 字段，process_single_request 在 rpc_recv
  后写入，各处理函数（含循环 recv 的 download_block/upload_block/file_stat/nc_extend）
  每次 rpc_recv 后刷新，供 ntoh 校验使用。

### 1.5 响应就地化组装（发送方向，同步纳入本次）

- hton 就地化：签名改为 `int msg_xxx_hton(msg_xxx_t *msg)`，业务直接组装到
  resp_net_buf（替代原 resp_host_buf 中间态），hton 就地转字段，消除 data memcpy。
- `rpc_send` 的发送长度须在 hton **前**取值（hton 就地会把 uiLEN 覆写为 wire 序）。
- **压缩路径**（download_block 响应 is_compress）：resp_host_buf 降级为压缩工作区
  （LZ4_compress_default 需源目标分离），压缩结果写回 resp_net->data 后发送。
- **解压路径**（upload_block/nc_extend 接收 is_compress）：net_buf 就地解析头，
  解压目标用 host_buf 工作区，块处理从工作区读取；无压缩路径完全就地零拷贝。

### 2. 协议层字节序切换为大端 → 小端

- rpc-protocol.cpp 全部 `htonl/ntohl/htonll/ntohll`（244 处）→
  `htole32/le32toh/htole64/le64toh`（<endian.h>，小端主机编译为空操作，
  大端自动 bswap，跨字节序安全）。
- rpc-msg.c 帧头 `get_u32/put_u32/get_u16/put_u16` → 小端解析
  （misc.c 已有 get_u32_le/put_u32_le；补 get_u16_le/put_u16_le）。
- 错误帧 body（rpc_send_err_frame 的 buf_put_u32）→ 不新增 buf LE 变体：
  用 misc 的 `put_u32_le` 写 4 字节临时区再 `buf_put`（buf 层 PEEK_U32/POKE_U32
  保持大端原样，rdbcomm 等共用方不受影响，buf 库零改动）。
- rpc-io.cpp 长度前缀（ntohl/htonl）、rpc-common.cpp 目录树打包 htonl → 同步切小端。
- **magic 陷阱**：'FSBC'=0x46534243 以 get_u32 大端读，切小端后需按字节序无关
  比较（memcmp "FSBC"）或适配常数，保证跨机校验正确。
- rpc-metadata.h 已小端，不动（一致性反而提升）。

### 3. 版本与升级

- `RPC_FRAME_VERSION` 2 → 3（wire 字节序破坏性变更，新老混跑返回
  RPC_ERR_PROTO_VERSION，复用 T0211 已定"同步升级不做多版本并存"策略）。
- **字节序显式承载于版本号**（借鉴 ZFS blkptr"字节序可检测"思想；rpc 有 version
  字段，无需 ZFS 式借位 bit）：version=3 语义即"小端 wire 协议常量"。接收端
  rpc_frame_parse 的 version 校验同时充当**字节序门禁**——version=2 的旧大端帧
  返回 RPC_ERR_PROTO_VERSION，绝不按小端静默误解析。
- 不采用"帧头 flags 借位 LE bit"：与 version 冗余（ZFS 用 bit 因其块结构无版本
  字段；rpc 的 version 已天然承载字节序信号），双信号源徒增维护负担。
- 演进路径：未来若需兼容旧端，按 version 分派解析路径（version=2 走大端解析），
  本次沿用同步升级策略不做多版本并存。
- 两端同仓库同步升级；aio-speed 客户端随同步。

## 用户故事

1. 作为 rpc 维护者，我想要对端变长字段长度被校验，以便恶意帧不能越界读写。
2. 作为 rpc 维护者，我想要协议字节序统一小端，以便与 metadata 层一致、对齐备份工业实践、小端平台零成本。

## 实现决策

- 修改模块：
  - rpc/rpc-protocol.{h,cpp}：全部 msg_*_hton/ntoh + dir_tree 系就地化（hton 单参就地、
    ntoh (msg, net_len) 就地校验）；file_stream_meta/file_stat/data_block 为 buf 内嵌
    结构保持双参不变
  - rpc/rpc-server.cpp：分发层就地解析 msg_base + uiLEN 预检 + 各分支调用点单缓冲
    （host=net=net_buf，resp 组装 resp_net_buf）；woker_info 增加 msg_len 字段；
    压缩/解压路径用 host_buf/resp_host_buf 作工作区
  - rpc/rpc-msg.c：帧头小端 + magic 适配
  - libs/misc.{c,h}：补全 LE 工具 get_u64_le/put_u64_le/get_u16_le/put_u16_le
    （get_u32_le/put_u32_le 已有）；**buf 层不做任何 LE 变体**，小端写用
    `put_u32_le` + `buf_put` 临时字节，buf 库零改动
  - rpc/rpc-io.cpp、rpc/rpc-common.cpp：长度前缀/目录树打包小端
  - rpc/rpc-msg.h：RPC_FRAME_VERSION 3
  - 客户端 rpc-client.cpp / rpc.cpp / rpc-command.cpp / rpc-public.cpp 调用点单缓冲就地
  - libs/rpc-net-protocol.c / libs/rpc-net.c：msg_get_time 系就地化同步
- 对外 API 合约：hton/ntoh 签名变化（破坏性，仅本仓库内调用方）。
- 缓冲治理：host_buf/resp_host_buf 保留（woker 结构不变），职责从"解码副本/组装中间态"
  降级为"压缩/解压工作区"；常规路径单缓冲零拷贝。
- 架构决策：ADR-0015（协议层字节序统一小端）+ 就地化（消除收发方向 data memcpy）。
- 不引入序列化框架（调研结论：备份程序均自定义紧凑二进制）。

## 测试决策

- 扩展 `tests/protocol_roundtrip.cpp`：全部消息往返字节级一致（按新小端 wire）。
- 新增恶意帧测试：超长变长字段 / 截断帧 / uiLEN 与实际不符 → 拒绝且无越界读写
  （Valgrind/ASAN 可观测）。
- 既有 `rpc/tests/*` 全过 = 回归基线。

## 验收标准

- [ ] AC-1: 全部 msg_*_ntoh 就地化（签名 `(msg, size_t net_len)`，就地转换 + 校验，返回 0/RPC_ERR_BAD_FRAME）
- [ ] AC-1b: 全部 msg_*_hton 就地化（单参），常规路径收/发方向均无 data memcpy（host/net 单缓冲）
- [ ] AC-2: 超长变长字段（cmd_len/path_len/name_len/key_len/data_len 等）被拒绝，无越界读写（恶意帧测试通过）
- [ ] AC-3: 服务端分发层校验 uiLEN ≤ 实际读入字节数，不符拒绝连接
- [ ] AC-4: rpc-protocol.cpp 全部 htonl/ntohl/htonll/ntohll 替换为 htole32/le32toh/htole64/le64toh，无残留大端转换
- [ ] AC-5: rpc-msg.c 帧头解析/组装切换为小端，magic 'FSBC' 跨机校验正确
- [ ] AC-6: 错误帧 body 随协议切小端（misc LE 工具 + buf_put 临时字节生效，buf 层不改动）
- [ ] AC-7: rpc-io.cpp 长度前缀、rpc-common.cpp 目录树打包同步小端
- [ ] AC-8: RPC_FRAME_VERSION 提升至 3，新老版本混跑返回 RPC_ERR_PROTO_VERSION
- [ ] AC-9: protocol_roundtrip 测试全过（按新小端 wire 往返字节级一致）
- [ ] AC-10: 全量 xmake test 回归通过（含既有 rpc/tests 基线）

## 范围外

- 帧头协议结构改动（T0211 已定稿）
- 引入通用序列化框架（调研明确不做）
- 大块传输零拷贝（③子项，另行评估）
- rdbcomm 等其他模块（仅 rpc 协议层）
- 多版本协议并存（沿用同步升级策略）
- **布局对齐/padding 重设计（不采纳）**：C 隐式 padding 布局脆弱（ABI/编译选项/
  成员增删均无声破坏 wire），且 rpc 变长嵌套含第二层变长（file_stat_item 的
  f_name），对齐 int64 无法定义整体 byteswap 边界；紧凑显式布局 + 逐字段转换是
  本项目正确形态。
- **协议 v4 候选（ZFS 模式，不在本次）**：定长结构体 + 定长元素数组（ZAP chunk
  式变长切碎）+ 每类型就地 byteswap 回调 + 结构体冻结治理。本次小端切换为 v4
  必经前置（v4 起步即小端，免二次迁移）。

## 备注

- knowledge 依据：`data-formats/backup-tools-serialization-practice.md`（已沉淀）、
  `debugging/c-buffer-api-size_t-frame-validation.md`
- 字节序陷阱：magic 按字节序列比较避免切端失效；buf 层 PEEK/POKE 大端保持原样
  （rdbcomm 等共用方依赖），小端写走 misc LE 工具 + buf_put 临时字节
- ZFS byteswap 机制对照（设计依据）：磁盘布局=内存布局 + blkptr 借位字节序标记 +
  每类型 byteswap 回调 + 变长定长化。rpc 因 wire≠内存布局（紧凑+变长）不照搬
  "就地翻转"，采纳其"字节序可检测/显式声明"与"每类型一个转换单元"思想。
- 就地化设计依据：小端主机上 wire 字节序=主机序，net_buf 强转即直接可用，
  ntoh/hton 从"拷贝+转换"降级为"就地转换+校验/编码"，消除 host_buf/resp_host_buf
  中间态的整段 data memcpy；大端主机 le32toh/htole32 自动 bswap，跨端一致。
  压缩/解压因 LZ4 源目标不可重叠，保留 host_buf/resp_host_buf 作工作区。
