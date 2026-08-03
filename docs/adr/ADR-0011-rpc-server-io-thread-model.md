# ADR-0011: rpc 服务端 IO/线程模型 — 单 Reactor + 工作线程池（对齐 Netty/muduo）

- 日期: 2026-08-03
- 状态: 已确认

## 背景

rpc 服务端为 thread-per-connection（`create_thread` 分离线程，无池、无上限）+ 阻塞 accept + 阻塞 IO + poll 单 fd 超时。连接数 = 线程数，恶意连接可耗尽资源；无连接管理、无统一超时。

## 决策

- 主线程 epoll 事件循环（水平触发）：listenfd accept + 连接可读事件 + 超时管理（`epoll_wait timeout = 最近 deadline`，不用 timerfd）
- 有界工作线程池（默认 = CPU 核数，rpc-config `max_workers`），执行请求处理
- **有界任务队列**（容量 = max_conn，对齐 SafeRPC in_flight 限制）：队列满拒绝新任务/关闭对应连接，防内存膨胀
- 连接上限（默认 8，rpc-config `max_conn`），超限 accept 后立即关闭；内存预算 <2GB
- **连接所有权转移**：worker 处理期间独占连接，事件循环不碰；处理完归还（避免 use-after-free）
- 事件循环线程内禁止阻塞操作；大帧按实际 total_len 分配
- 每连接请求保持串行（响应顺序语义不变）；不同连接由线程池并行
- 现有 30+ 个同步处理函数不动，事件循环只做调度
- 优雅关闭：连接从 epoll 移除、线程池 drain、listen 停止

## 权衡

- 备选：有界线程池 + 阻塞 IO（Tomcat BIO 风格）—— 放弃（用户要求完整对齐工业）
- 备选：每核多 Reactor（Netty 主从）—— 放弃（本场景连接数少，单 Reactor 足够且更简单）
- 备选：客户端异步化 —— 放弃（业务层 3283 行同步调用链，收益为零）
- 备选：任务队列无界 —— 放弃（内存无界；有界 + 满拒绝对齐 SafeRPC in_flight）

## 影响

- 重构位置：`RpcService::RPCServiceThread` 调度循环 → rpc-epoll 模块；`StartRPCServiceWoker` 改为单次请求处理
- 客户端保持同步 API + 内部非阻塞（传输层）
