# T0222 rpc-epoll 对接业务：回调 + 状态机重构

## 问题陈述

rpc-epoll 调度层（T0213/T0214/T0215 完成）已具备成熟事件循环骨架，但**未真正对接业务**：

1. `rpc_conn_handler` 是"连接级一次性回调"：epoll 事件 → worker 出队 → 调用 handler 一次 → 归还。
2. `rpc_epoll_conn_handler`（rpc-server.cpp L360）把连接 fd 强制恢复阻塞模式（L394-398），同步调用 `process_single_request`。
3. `process_single_request`（L152，206 行）巨型分发：rpc_recv 阻塞读完整请求 → 同步处理 → 写回，17 个 MT_* 分支。业务无状态机、无半包缓冲、无分段处理。
4. 客户端（rpc.cpp 13+ 处 rpc_conn_recv_msg、do_scp_*、fs-backup）全部同步阻塞。
5. 结果：epoll 仅用于 accept+分发，业务实质是"每连接一 worker 阻塞式同步服务器"。长耗时业务独占 worker。

## 决策（用户确认，P2 Grill 记录于 clarifications.jsonl）

1. **重构范围：服务端 + 客户端都重构**（彻底异步化，wire 格式不变）
2. **客户端形态：全部一次性重写**（rpc.cpp / do_scp_* / fs_backup 全改回调式）
3. **worker 模型：去 worker 纯事件驱动**（单线程事件循环，类似 node.js/redis；事件回调驱动状态机，无业务线程独占）
4. **TLS 异步化纳入本任务**（非阻塞 SSL_accept + 事件驱动，否则握手阻塞事件循环）

## 重构目标

- **事件级回调**：epoll 层提供 readable/writable/close 事件回调，替代连接级一次性 handler
- **纯事件驱动**：去掉 worker 池，业务全部在 reactor 线程事件回调中执行（短任务快速推进，无阻塞调用）
- **状态机驱动**：每个连接持有协议状态机（半包缓冲 + 帧解析状态 + 业务子状态），事件驱动推进
- **连接保持非阻塞**：删除 rpc_epoll_conn_handler 的阻塞模式恢复
- **客户端异步化**：rpc_conn_* / do_scp_* / fs_backup 重写为回调式异步 API
- **大块传输分段化**：SCP 流分段读写（read/write 可重入），事件驱动推进
- **保持协议兼容**：wire 格式不变（T0217 小端已落地），仅重构处理架构

## 已知信息

- epoll 层：`rpc_conn_handler` 签名 `int (*)(int connfd, void *ctx)`（rpc-epoll.h L25）
- worker_main L349 一次性调用 handler；`keep!=0` 关闭连接，`keep==0` 归还重挂 EPOLLIN|ONESHOT
- epoll 层仅挂 EPOLLIN|EPOLLONESHOT（L365/L446），无 EPOLLOUT 支持（需新增）
- 连接上下文 `rpc_service_woker_info`（conn_ctx_get/put/remove）
- TLS：tls_cert_server_handshake 同步 SSL_accept（rpc-server.cpp L403）
- 客户端调用面：rpc.cpp 13+ 处 rpc_conn_recv_msg、rpc-command.cpp do_scp_download/upload（rpc_recv_frame 循环）、fs-backup/fsdeamon/fs_service.cpp rpc_recv/rpc_send
- 既有测试：rpc_server_epoll_integration（65 PASS）、scp_stream（509 PASS）、multi_reactor、conn_limit、heart_beat、bench_*（全部基于当前阻塞 handler，重构后需重写适配）
- T0217 已切协议层小端 + 帧头字节序无关 magic，wire 稳定

## 信息缺口（P1 已解部分）

- ~~重构范围边界~~ → 服务端+客户端都重构（用户确认）
- ~~客户端形态~~ → 全部一次性重写（用户确认）
- ~~worker 模型~~ → 去 worker 纯事件驱动（用户确认）
- ~~TLS 异步化~~ → 纳入本任务（用户确认）
- 剩余：SCP 流式状态机与现有 STREAM 帧协议/长度前缀对接的具体设计；epoll 事件接口最小形态；测试重写策略

## 验收标准（P2 更新版）

- [ ] AC-1: epoll 层提供事件级回调（readable/writable/close），替代连接级一次性 handler
- [ ] AC-2: 去掉 worker 池，业务在 reactor 线程事件驱动中执行（纯事件驱动，无业务线程独占）
- [ ] AC-3: 业务协议解析改为状态机（半包缓冲 + 帧解析状态 + 业务子状态）
- [ ] AC-4: 连接 fd 保持非阻塞，删除 rpc_epoll_conn_handler 的阻塞模式恢复
- [ ] AC-5: process_single_request 巨型分发重构为按消息类型的处理函数注册表/回调
- [ ] AC-6: 大块传输（SCP 流）分段读写，事件驱动推进
- [ ] AC-7: 客户端异步化：rpc_conn_* / do_scp_* / fs_backup 重写为回调式异步 API
- [ ] AC-8: TLS 握手异步化（非阻塞 SSL_accept + 事件驱动）
- [ ] AC-9: 全量回归通过（rpc_server_epoll_integration/scp_stream 等适配后全绿）
- [ ] AC-10: 性能不劣化（bench_download/bench_concurrent/RPS 与 T0215 基线对比）

## 风险

- 纯事件驱动下 CPU 密集任务阻塞事件循环（bench_rps 的 echo 场景不受影响，但加密/校验和密集操作需评估）
- 客户端一次性重写影响面大，需同步迁移所有调用方
- TLS 异步化（SSL_read/SSL_write 非阻塞）复杂度高，需保留非 TLS 路径回归保障
