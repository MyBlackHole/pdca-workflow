# backupstream 80.0.0 架构对照：plain/TLS 双路径 ingress 与线程模型

来源: records/T0287-0815-backupstream-architecture/conclusion.md

## 核心模式

1. **plain/TLS 双网络主线**：非 TLS 用"main reactor + 弹性会话池 + EXEC 共享事件域"；
   TLS 用"Reactor Group 分片 + 非阻塞 TLS 状态机"。两条主线刻意分离，互不混用。

2. **业务前握手段事件化（v80）**：接受连接 → 非阻塞 ingress 状态机
   （WAIT_HELLO→SEND_HELLO_ACK→WAIT_OPEN）解析 HELLO/认证/首个操作帧，
   再恢复阻塞模式移交会话池。慢客户端只占连接槽，不占业务线程——
   "admission 两层分离"：`max_sessions`（连接槽）≠ `session_queue/workers`（业务线程槽）。

3. **弹性会话池**：`--session-workers` 是上限而非固定值；worker 按队列压力创建
   （spawn 前先发布 live_workers），空闲 `pthread_cond_timedwait` 超时自我退出。
   EXEC handoff 后 worker 立即退休（除非有排队工作），避免空转。

4. **进程级共享 EXEC 事件域**：一个 shard 用 event_waiter 多路复用多个子进程
   管道 + 唤醒管道 + socket 可写性；慢消费者只背压自身子管道，不阻塞 shard。
   轻载 shard（≤4 会话）用更小预算。shard 数 auto = ceil(max-exec/64)，≤8，≤CPU。

5. **事件原语**（reactor_t）：`epoll_event.data.u64 = generation:32|slot:32`
   防失效；interest 更新合并（回调执行期延迟 MOD，返回时最多一次）；
   HIGH/NORMAL 双 post 队列 + eventfd 唤醒；单 timerfd + 最小堆逻辑定时器；
   回调预算限流。通用等待原语 `event_waiter_t` 提供 epoll/poll 双后端。

## 陷阱与边界

- **worker 供给与连接数匹配**：多 Reactor 分片下若每分片 worker 全额放大，
  低并发会因空闲线程调度开销反而退化（参见 multireactor-so-reuseport）。
  backupstream 用弹性创建 + idle 回收规避此问题。
- **ingress 读预算必须存在**：无预算的单连接可独占 main reactor（64 KiB 预算）。
- **TLS 显式 WANT 重试归属**：`SSL_read→WANT_WRITE` 给 RX 独占重试权；
  `SSL_read→WANT_READ` 不阻塞应用写，保持全双工。
- **慢消费者背压隔离**：会话池 worker 背压只在自身队列/子管道，不影响共享 shard。

## 验收信号

- 慢客户端压测下业务线程数不增长（v80 验证：256 个单字节 HELLO 客户端，
  Agent 线程数 33→1，正常 caps 请求从超时恢复到 3ms 级）是"ingress 事件化有效"的信号。
- 弹性池有效性信号：活跃业务 session 数下降后线程数能回收（1→9→1）。
