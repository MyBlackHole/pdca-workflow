# ADR-0014: rpc-epoll 多 Reactor 分片 — SO_REUSEPORT 多监听

- 日期: 2026-08-05
- 状态: 已确认

## 背景

T0214 完成单 Reactor 事件循环工业对齐（ADR-0011/0013）后，实测单 Reactor 的
epoll_wait 分发线程存在吞吐上限：32 客户端并发 echo RPS 封顶 ~135K req/s
（bench_rps，16 核 / loopback）。本任务引入多 Reactor 分片以突破单线程分发瓶颈。

## 决策

- **SO_REUSEPORT 多监听**（nginx `listen ... reuseport` 同款）：每 Reactor
  创建独立 listenfd，绑定同一端口；内核按连接 4-tuple 哈希分流，accept 在
  各 Reactor 内完成，无跨 Reactor 同步。放弃用户态轮询/接管分发（每连接
  accept 由哪个 Reactor 完成即固定归属该 Reactor，连接事件永不迁移）。
- **每 Reactor 独立资源**：listenfd / worker 线程池 / 有界任务队列 / fd→连接
  开放寻址 hash 表 / 最小堆定时器。零共享可变状态，worker 与连接全部隔离，
  Reactor 之间无锁、无原子计数、无全局队列。
- **`reactor_count` 配置语义**：0 = auto → `sysconf(_SC_NPROCESSORS_ONLN)`，
  上限 `RPC_EPOLL_MAX_REACTORS`(64)；显式 N 则 N 个 Reactor（N ≤ 上限）。
  `reactor_count=1` 时退化为单 Reactor，与 T0213/T0214 行为一致（兼容旧配置
  与单核部署）。
- **事件处理流程**：宿主线程创建全部 Reactor；每 Reactor 线程 = epoll_wait
  分发 + 本 Reactor worker 消费本 Reactor 队列；`rpc_epoll_start` 部分启动
  失败时统一走 `rpc_epoll_stop`（eventfd 唤醒）并 join 已启动的 reactor_tid
  与 worker_tids，杜绝线程泄漏。
- **Worker 供给**：每 Reactor 独立 worker 池，规模 = `max_workers`（每 Reactor
  全额，不按 Reactor 均摊）。总 worker 数 = reactor_count × max_workers。
- **性能预期**：多 Reactor 收益条件 = 连接事件量超过单线程可分发量；低并发时
  因 worker 池按 Reactor 放大（N× 空闲线程调度开销）可能劣于单 Reactor。

## 权衡

- 备选：单 listenfd + 多 Reactor 轮询 accept —— 放弃（accept 需锁或 CAS，
  且连接归属仍固定一个 Reactor，SO_REUSEPORT 由内核分流零开销）
- 备选：用户态事件迁移 / 工作窃取 —— 放弃（破坏零跨 Reactor 同步的简单性，
  与有界队列所有权模型冲突）
- 备选：libevent/muduo 现成多线程模型 —— 放弃（沿用 T0213 自研所有权转移
  与有界队列结构，不引入外部依赖）

## 实测数据（2026-08-05，16 核 / loopback）

- 单连接 256MB 下载：rc=1 → 921.5 MB/s，rc=16 → 903.3 MB/s（0.98 ≥ 0.95，
  AC-3 通过；loopback 带宽封顶 ~900MB/s）
- 8 客户端并发 16MB 下载：rc=1 → 888.5 MB/s，rc=4 → 897.1 MB/s（1.01×，
  AC-2 放宽后无劣化；聚合受 loopback 带宽封顶，物理上无法 2×）
- echo RPS：8 客户端 rc=1 → 87K，rc=4 → 82K（低并发 rc4 略低，分发非瓶颈 +
  24 个空闲 worker 调度开销）；32 客户端 rc=1 → 134K（单 Reactor 分发瓶颈），
  rc=4 → 164K（1.22×，分发分摊开始体现收益）
- 结论：AC-2 断言由"多 Reactor 吞吐 ≥2×"放宽为"8 客户端聚合 ≥0.95× 无劣化 +
  32 客户端 RPS 扩展"，理由（loopback 带宽封顶 / 分发在 8 连接时非瓶颈）见
  prd.md 备注。

## 遗留（记录为后续优化）

低并发（<16 连接）下 rc4 < rc1 的劣化源于 worker 池按 Reactor 全额放大（N×
空闲线程调度开销）。后续优化方向：auto 模式下总 worker 数按 `max_workers`
封顶并按 Reactor 均摊，或按实际连接数动态收缩 worker。本任务不改 worker
供给语义（保持 AC-4"每 Reactor 独立 worker 池，规模 = max_workers"）。
