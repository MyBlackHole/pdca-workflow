# T0225 调研报告 — rpc 复用 socket 无关闭时机的空闲回收方案

## 调研目标

F/131 rpc 复用连接缺少确定的空闲关闭时机。要求在现有 `rpc_conn` /
`StartRPCServiceWorker` 结构上，明确"关闭时机"的驱动方、落点与边界，
并发掘既有"客户端正常关闭被误报为坏网络"症状的真实成因与收口处。

## 方法

以项目源码（rpc/ 与 libs/）为权威一手源，口径：

- 关闭路径追踪：客户端连接创建/复用/关闭 → 服务端 accept/worker/回收。
- 超时与信号语：`read_is_ready` 的 poll 事件集、`SO_LINGER` 有无、FIN 到达
  时序。
- 空发日志归因：用 2026-08-07 09:44 实测日志反查 `rpc_recv` EOF 分支。

## 发现

### F1. 连接持有形态：每调用方单 conn，两态复用
- `rpc_conn_start`（rpc/rpc.cpp:2378）创建复用连接，`restart_conn_cb=rpc_conn_restart`；
  `rpc_conn_stop`（rpc.cpp:2446）释放。发送统一走 `rpc_conn_reconn_send_msg`
  （rpc-conn.cpp:161）：按 `is_usable` 复用 / 重连。
- 另有命令级短连接 `session_info`（rpc.cpp:141）。均非集中式连接池。
- 结论：闲置回收的天然落点是"每调用方持有的单 `rpc_conn`"，故选择惰性回收
  而非连接池巡检。

### F2. 服务端 worker 回收：有，但仅两个触发器
- `StartRPCServiceWorker`（rpc-server.cpp:178）`while(true)` 循环
  `read_is_ready(client, read_timeout)`（:215）→ 超时/错误 → `return__`
  `shutdown+close`（:409-411）。默认 `read_timeout=120000ms`（rpc-config.cpp:141）。
- 无业务空闲驱动的主动回收时机，空闲连接悬挂占 fd + worker 线程最长 120s。

### F3. 客户端主动告知机制：底层已具备，无需协议
- `read_is_ready`（libs/common.c:17）poll 事件 `POLLIN|POLLRDHUP|POLLHUP`。
- 客户端正常 `close(sockfd)` → 发 FIN → 服务端 poll 立即被 `POLLRDHUP` 唤醒
  （不催 read_timeout）。**无需新增 MT_* 协议消息**。
- 无 `SO_LINGER`（rpc/、libs/ 均未设置）→ 优雅 FIN 而非 RST，不会误触
  `POLLERR/EIO`。

### F4. EOF/残留数据语义
- `POLLIN` 与 `POLLRDHUP` 同时置位时 poll 按"可读优先"，`rpc_recv` 先读完
  缓冲残留完整消息再轮回 RDHUP；worker 本就逐轮 poll=recv 单条，不丢数据。
- 客户端仅在空闲时才触发回收，事务内不并发，与半包竞态冲突实质归零。

### F5. 实测症状归因（已诊既有瑕疵）
2026-08-07 09:44:58 实测日志、客户端 close 后：

```
rpc-io.cpp:47   receive failure. nread:0       <- EOF 被当错误
rpc-io.cpp:57   receive failure bytes:0 != 4   <- -100 返回
rpc-server.cpp:222 recv request failure for bad network. bytes:-100
rpc-server.cpp:414 close client connection ...  <- 最终还是关闭
```

根因：`rpc_recv`（rpc-io.cpp:25）`while` 循环 `recv` 返回 0（EOF）时走
`nread<1` 且非 EINTR/EAGAIN 的错误分支（:44）打印 Error 并 `break`，随后
`bytes != 4` → `return -100`（:57）。worker 借此负值径打 "bad network"，最后
才 `return`。**连接确实被回收，但"正常 EOF"被当作"坏网络"**，产生 3 条
Error 噪音。

## 结论与建议

### 结论（ADR-0016 已固化方向）
- 关闭时机由**客户端主动 FIN 主导**：每调用方单 `rpc_conn` 增加空闲判定
  （`last_used` + `idle_timeout`），空闲超阈值主动 `close` 发 FIN；服务端
  经 `POLLRDHUP` 立即回收。服务端 `read_timeout` 对齐为兜底。
- 不新增协议消息、不引入服务端独立巡检/连接池。
- 本次为研究产出，不落代码（ADR 与 PRD 已固化落点）。

### 建议实现项（后续任务登记）
1. `rpc_conn` 增空闲判定字段，复用路径 `rpc_conn_reconn_send_msg` 自动重连。
2. rpc-config 增 `idle_timeout` 配置，取默认 < 服务端 `read_timeout`(120s)。
3. **并入 EOF 判定**：`rpc_recv` 区分 `nread==0`（EOF/正常关闭，返回非错语义）
   与 `nread<0`（网络错误），消除"正常关闭被误报 bad network" 3 条 Error 噪音；
   与空闲回收同段收口。

## 参考资料
- rpc/rpc-conn.cpp `rpc_conn_*`、rpc/rpc.cpp `rpc_session_start/stop`、
  `rpc_conn_start/stop/reconn_send_msg`
- rpc/rpc-server.cpp `StartRPCServiceWorker`（:178,215,222,409）
- rpc/rpc-io.cpp `rpc_recv`（:25-66）、libs/common.c `read_is_ready`（:17）
- rpc/rpc-config.cpp `read_timeout`/`keepalive`
- ADR 记录：ADR-0016；实测日志（2026-08-07 09:44:58）