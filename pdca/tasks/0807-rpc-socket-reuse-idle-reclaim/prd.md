# T0225 PRD — rpc 复用 socket 无关闭时机的空闲回收方案

## 问题陈述

- **现状**：F/131 rpc 复用连接无确定空闲关闭时机。客户端仅出错/重连触发
   `rpc_conn_close`；服务端 `StartRPCServiceWorker` 仅由 `read_is_ready`(120s)
   或对端 FIN 触发 `return__` 关闭（rpc-server.cpp:215,409）。业务空闲的连接
   悬空占 fd 与服务端 worker 线程，无主动回收。
- **已诊既有瑕疵**：客户端正常 `close`（FIN）到达服务端时，`rpc_recv` 把
  EOF（`nread==0`）误判为网络错误，打印 `receive failure nread: 0`（rpc-io.cpp:47）、
  `receive failure bytes: 0 != 4`（rpc-io.cpp:57）并 `return -100`，worker 再打
  `recv request failure for bad network`（rpc-server.cpp:222）后走 `return__`。
  虽最终关闭，但产生 3 条 Error 噪音，且关闭被错误归因为"坏网络"而非正常 EOF。
- **目标**：明确"关闭时机"的驱动方与落点，使空闲连接在可控时机回收，
  不靠理论无限等待。
- **差距**：缺客户端主动、业务空闲驱动的关闭决策点；服务端缺独立空闲回收
  通道（仅超时兜底）。

## 解决方案

以**客户端主动 FIN 为主导**：客户端复用 `rpc_conn` 在业务空闲超阈值时主动
`close`，经既有 `POLLRDHUP` 通道让服务端 worker 立即回收；服务端
`read_timeout` 作为对齐兜底，不加协议、不加连接池巡检。本次仅固化方案/选型，
不落代码。

**并入的既有瑕疵处置**：`rpc_recv` 应区分 `nread==0`（对端正常 FIN/EOF，返回
EOF 语义）与 `nread<0`（网络错误），使 worker 对正常关闭不再误报 "bad
network" 并减少 Error 噪音；与"该关没关"症状收口于同一处（rpc_recv /
StartRPCServiceWorker）。

## 用户故事

1. 作为复用长连接调用方，我希望空闲连接在阈值内自动回收，以便不无限占 fd。
2. 作为服务端 worker，我希望客户端"不用了"能及时驱动我关闭，而非等到
   read_timeout 超时，以便释放线程与 fd。
3. 作为运维，我希望关闭时机可配置且两端超时语义清晰，避免一方抢先关闭。

## 实现决策

- 客户端 `rpc_conn` 增加空闲判定（`last_used` + `idle_timeout`），期满主动
  FIN；复用路径 `rpc_conn_reconn_send_msg` 自动重连。
- 服务端 `StartRPCServiceWorker` 维持 `read_timeout` 兜底，确认取值对齐
  （客户端更早触发）。
- 不新增协议消息（底层 `POLLRDHUP` 已承载对端关闭信号）。
- 交付为研究产出，不改代码。ADR-0016 固化方向。

## 测试决策（后续实现期）

- 实现的验收应覆盖：客户端空闲超时主动 close → 服务端 worker 在
  `read_timeout` 内提前回收（而非等满 120s）；重连后复用正常；fd 不泄漏。

## 验收标准

- [ ] AC-1: 完成方案选型，明确关闭时机驱动方（客户端 FIN 主导）
- [ ] AC-2: 明确服务端 StartRPCServiceWorker 兜底与客户端空闲超时对齐关系
- [ ] AC-3: 产出 ADR-0016，固化决策方向与实现落点
- [ ] AC-4: 明确配置项（idle_timeout）与默认值的对齐约束（< read_timeout）
- [ ] AC-5: 验证 POLLRDHUP 触发前提（无 SO_LINGER、close 发 FIN、POLLIN 优先读取）成立
- [ ] AC-6: 确认 EOF（nread==0）与网络错误（nread<0）的判定语义区分已纳入收口设计

## 技术前提验证（P2 终审补充）

- **POLLRDHUP 必然性**：客户端 `close()` 发 FIN（无 SO_LINGER，rpc/libs 均未
  设置，本轮已核实）→ 服务端 poll 触发 `POLLRDHUP|POLLHUP`，`read_is_ready`
  返回 1，无需等 read_timeout。优雅关闭而非 RST，不误判 POLLERR/EIO。
- **POLLIN 与 POLLRDHUP 并存**：二者同时置位时 poll 按可读优先，`rpc_recv`
  先读完缓冲残留的完整消息再轮回 RDHUP，不会丢未取数据；worker 本就
  `while(true)` 每轮 poll=recv 单条，协议自洽。
- **空闲 FIN 边界**：客户端事务内不并发（空闲超时才触发 FIN），与半包竞争
  实质归零；rpc_recv 在无数据收到 FIN 时返回 -100 并记一条 receive failure
  ErrorLog（rpc-io.cpp:44）后正常 goto return__，不挂死（日志噪音为已知瑕疵，
  后续实现可优化）。

## 范围外

- 不实现代码（不修改 rpc/rpc-conn.*、rpc.cpp、rpc-server.cpp）
- 不做服务端独立空闲巡检线程 / 连接池
- 不新增协议消息类型
- 不涉及 epoll worker 供给（T0216 范围）

## 备注

- 复用连接持有形态已核实为"每调用方单 conn"，两态并复用
  （session_info 免责周期连接 + rpc_conn 长复用）。
- 服务端 `return__` 已有 `shutdown+close`，回收座位仅触发时机单一。