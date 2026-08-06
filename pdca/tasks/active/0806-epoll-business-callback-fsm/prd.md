# T0222 rpc-epoll 对接业务：回调 + 状态机重构

## 问题陈述

rpc-epoll 调度层（T0213/T0214/T0215 完成，含 ONESHOT 事件、有界队列、
worker 池、定时器堆、fdmap）已具备成熟事件循环骨架，但**未真正对接业务**：

1. `rpc_conn_handler` 是"连接级一次性回调"：epoll 事件 → worker 出队 → 调用
   handler 一次 → handler 返回后归还连接。
2. `rpc_epoll_conn_handler`（rpc-server.cpp L360）在 handler 内把连接 fd
   **强制恢复 O_NONBLOCK 清除（阻塞模式）**（L394-398），随后同步调用
   `process_single_request`。
3. `process_single_request`（L152，206 行）是巨型分发函数：`rpc_recv` 阻塞
   读完整请求 → 同步处理 → 写回，17 个 `MT_*` 分支。业务无状态机，无半包
   缓冲，无分段处理。
4. 结果：epoll 仅用于 accept + 分发，业务实质仍是"每连接一 worker 阻塞式
   同步服务器"。长耗时业务（大文件下载/上传）会长时间独占 worker，
   reactor_count 扩展只对短请求生效。

## 重构目标

- **事件级回调**：epoll 层提供 readable/writable 事件回调（替代连接级一次性 handler）
- **状态机驱动**：每个连接持有协议状态机（半包缓冲、帧解析状态、业务子状态），
  由事件驱动推进，不阻塞 worker
- **异步化**：大块传输（SCP 流）改为分段读写（read/write 可重入），worker 可
  被其他连接复用
- **保持协议兼容**：wire 格式不变（小端、T0217 已落地），仅重构服务端处理架构

## 已知信息

- epoll 层：`rpc_conn_handler` 签名 `int (*)(int connfd, void *ctx)`（rpc-epoll.h L25）
- handler 一次性调用：worker_main L349 `r->ep->handler(connfd, r->ep->handler_ctx)`
- ONESHOT 事件模型：`c->busy=1` 标记 worker 独占，事件循环不触碰（rpc-epoll.cpp L465-469）
- 业务分发：`process_single_request`（rpc-server.cpp L152-357），17 个 MT 分支
- 连接上下文：`rpc_service_woker_info`（conn_ctx_get/put/remove）
- TLS 握手在 handler 内同步完成（tls_cert_server_handshake）
- 既有测试：rpc_server_epoll_integration（65 PASS）、scp_stream（509 PASS）
  均基于当前阻塞式 handler，重构后需适配
- T0217 已切协议层小端 + 帧头字节序无关 magic，wire 稳定

## 信息缺口（P1 待核实）

- epoll 层需新增的最小事件接口形态（readable/writable 回调如何挂载到现有
  fdmap/ONESHOT 模型）
- 大块传输（SCP upload/download）状态机如何与现有 rpc_io/rpc-command 的
  长度前缀 + STREAM 帧协议对接
- worker 归还语义调整（busy 标记何时释放：状态机挂起 vs 完成）
- TLS 握手异步化是否纳入本任务范围
- 既有 509/65 测试如何适配新回调模型

## 验收标准（草案，待 P1 澄清）

- [ ] AC-1: epoll 层提供事件级回调（readable/writable），替代连接级一次性 handler
- [ ] AC-2: 业务协议解析改为状态机（半包缓冲 + 帧解析状态 + 业务子状态）
- [ ] AC-3: 连接 fd 保持非阻塞，删除 rpc_epoll_conn_handler 的阻塞模式恢复
- [ ] AC-4: process_single_request 巨型分发重构为按消息类型的处理函数注册表/回调
- [ ] AC-5: 大块传输（SCP 流）分段读写，worker 可被其他连接复用
- [ ] AC-6: 全量回归通过（rpc_server_epoll_integration/scp_stream 等适配后全绿）
- [ ] AC-7: 性能不劣化（bench_download/bench_concurrent 与 T0215 基线对比）
