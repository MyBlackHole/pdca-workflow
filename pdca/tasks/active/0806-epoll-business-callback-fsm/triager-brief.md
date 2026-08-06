# T0222 Triage Brief

## 分类

- category: enhancement（架构重构）
- scenario_type: development
- 来源：用户直接提出方向"epoll 应先对接业务，协议业务重构为回调+状态机"

## 查重结果

- T0218（buf 层字节序）因本任务暂停（plan 阶段保留，优先级让位）
- T0213/T0214/T0215（epoll 事件循环骨架）为本任务的前置基础
- 无已存在的 epoll 业务对接/状态机重构任务

## Claim 验证（代码事实）

1. `rpc_conn_handler` 连接级一次性回调：rpc-epoll.h L25 `int (*)(int connfd, void *ctx)`
2. worker_main 一次性调用：rpc-epoll.cpp L349 `handler(connfd, handler_ctx)`，ONESHOT + busy 标记
3. `rpc_epoll_conn_handler` 强制阻塞模式：rpc-server.cpp L394-398 清除 O_NONBLOCK
4. `process_single_request`：L152 起，206 行，17 个 MT_* 分支，rpc_recv 阻塞读+同步处理
5. 结论：epoll 仅用于 accept+分发，业务实质是"每连接一 worker 阻塞式同步服务器"

## 信息缺口

- epoll 层事件级回调的最小接口形态（readable/writable 挂载到 fdmap/ONESHOT）
- SCP 大块传输状态机与现有 STREAM 帧协议/长度前缀对接方式
- worker busy 释放语义调整（状态机挂起 vs 完成）
- TLS 握手异步化是否纳入范围
- 509/65 既有测试的适配工作量

## 推荐下一步

1. P1 澄清：重构范围边界（纯服务端？客户端同步改？TLS 是否纳入）
2. P2 Grill：状态机粒度（连接级 vs 消息级 vs 流式传输级）、worker 模型（保留池 vs 事件驱动协程）
3. P3 PRD：明确 AC 与分阶段（先事件回调，再状态机，后流式异步）
4. P4 拆解：epoll 事件接口 / 帧解析状态机 / 分发注册表 / SCP 流式状态机 / 测试适配
