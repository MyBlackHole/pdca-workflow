# ADR-0016: rpc 连接复用空闲回收 — 客户端主动 FIN 主导

- 日期: 2026-08-07
- 状态: 已确认（研究产出，仅固化决策方向，不改代码）

## 背景

F/131 rpc 复用连接无确定的空闲关闭时机。连接仅依赖两处回收：客户端侧
出错/重连路径的 `rpc_conn_close`（rpc.cpp），服务端侧 `StartRPCServiceWorker`
`while` 循环 `read_is_ready(client, read_timeout)`（rpc-server.cpp:215）
触发 `return__` 的 `shutdown+close`（rpc-server.cpp:409）。无业务空闲驱动
的主动回收时机，空闲连接会悬挂占用 fd 与服务端 worker 线程。

既有瑕疵：客户端正常 `close`（FIN）到达时，`rpc_recv` 将 EOF（`nread==0`）
误判为网络错误，产生 `receive failure nread: 0` / `bytes: 0 != 4`
（rpc-io.cpp:47,57）+ `recv request failure for bad network`
（rpc-server.cpp:222）共 3 条 Error 噪音后才关闭——"已关被判错"。

## 决策

- **以客户端主动告知为主导**：客户端复用连接在业务空闲超过阈值时主动
  `close(sockfd)`，发出 FIN。
- **不新增协议消息**：底层 `read_is_ready` 的 poll 事件已含
  `POLLRDHUP|POLLHUP`（libs/common.c:17），服务端会由 FIN 立即唤醒 worker，
  `rpc_recv` 读到 0 即走 `return__` 关闭。语义天然，协议零改动。
- **客户端空闲回收点**：单个复用 `rpc_conn` 增加空闲超时判定（默认
  `idle_timeout` < 服务端 `read_timeout`），期满主动 FIN，复用路径
  `rpc_conn_reconn_send_msg` 自动重连，无需客户端业务感知。
- **服务端侧整改**：`StartRpcServiceWorker` 的 `read_timeout` 作为既有兜底，
  确认其与客户端 `idle_timeout` 的取值对齐（客户端更早触发）；不新增独立
  空闲巡检与连接池。
- **交付形态**：本次为研究/选型产出，仅固化决策方向与落点，未落代码。
- **并收 EOF 判定**：`rpc_recv` 区分 `nread==0`（EOF，正常关闭）与 `nread<0`
  （网络错误），worker 对正常 FIN 不再误报 "bad network"，消除 3 条 Error
  噪音；与空闲回收同段收口，随实现一并处理。

## 权衡

- 备选：服务端独立空闲巡检（shutdown/close 空闲连接）—— 放弃。会打断
  客户端仍打算复用的连接，且需服务端自维护自持有表与定时任务。
- 备选：显式应用层结束消息（新增 MT_* 通知服务端）—— 放弃。语义虽显式，
  但 `POLLRDHUP` 信号已天然承载"对端关闭"，避免协议与双端新分支改动。
- 备选：仅依赖 TCP keepalive 探活 —— 放弃。keepalive 只查对端本机存活，
  不反映业务空闲，无法作为回收时机。

## 技术前提验证（终审确认）

- **POLLRDHUP 必然性**：客户端 `close()` 发 FIN（rpc/libs 未设 SO_LINGER，
  已核实）→ 服务端 poll 触发 `POLLRDHUP|POLLHUP`，`read_is_ready` 返回 1，
  无需等 read_timeout；优雅关闭而非 RST，不误判 POLLERR/EIO。
- **POLLIN 与 POLLRDHUP 并存**：同时置位时 poll 按可读优先，`rpc_recv` 先
  读完缓冲残留完整消息再轮回 RDHUP；worker `while(true)` 每轮 poll=recv
  单条，协议自洽，不丢数据。
- **空闲 FIN 边界**：客户端空闲超时才触发 FIN、事务内不并发，与半包竞争
  实质归零；`rpc_recv` 无数据收到 FIN 返回 -100 并记一条 receive failure
  ErrorLog（rpc-io.cpp:44）后正常 goto return__，不挂死。

## 遗留（登记后续实现）

- 实现时需在 rpc-config 增加 `idle_timeout` 配置项，并确认其默认取值
  < 服务端 `read_timeout`（当前 120000ms）。
- `StartRPCServiceWorker` 的回收日志（`InfoLog` return__ 关闭）可补充
  "空闲超时回收"可观测标记。