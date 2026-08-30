---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop-multireactor-so-reuseport
type: domain
layer: Knowledge
status: active
summary: 多 Reactor 分片：SO_REUSEPORT 多监听（nginx reuseport 同款）
domain:
- ontology:domain/linux-epoll-eventloop
relations:
  specializes:
  - ontology:domain/linux-epoll-eventloop
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 多 Reactor 分片：SO_REUSEPORT 多监听（nginx reuseport 同款）

来源: records/T0215-0804-rpc-epoll-multireactor/conclusion.md

## 核心模式

1. **SO_REUSEPORT 多监听**：每 Reactor 创建独立 listenfd 绑定同一端口，
   内核按连接 4-tuple 哈希分流，accept 在各 Reactor 内完成。无用户态
   分发/接管，无跨 Reactor 同步。比"单 listenfd + 多 Reactor 轮询 accept"
   更简单（无需锁/CAS），由内核零开销分流。
2. **每 Reactor 独立资源**：listenfd / worker 线程池 / 有界任务队列 /
   fd→连接 hash 表 / 最小堆定时器。零共享可变状态 → Reactor 间无锁、无
   原子计数、无全局队列。连接事件永不迁移（accept 归属即固定）。
3. **reactor_count 配置语义**：0 = auto → `sysconf(_SC_NPROCESSORS_ONLN)`，
   设上限；显式 N 退化为单 Reactor 时行为与旧实现一致（兼容旧配置）。
   宿主线程创建全部 Reactor，部分启动失败统一走 stop（eventfd 唤醒）+ join
   已启动线程，杜绝线程泄漏。
4. **收益条件**：多 Reactor 的收益 = 连接事件量超过单线程 epoll_wait 可分发
   量。单分发线程有吞吐上限（实测 echo RPS ~135K req/s），32 客户端时
   4 Reactor 反超 1.22×。

## 陷阱：worker 池按 Reactor 全额放大

`每 Reactor worker 池规模 = max_workers` 时总线程 = reactor_count × max_workers。
低并发（<16 连接）下 4×8=32 worker 中 24 个空闲，futex 等待/唤醒调度开销使
rc4 < rc1（8 客户端 RPS 0.94×）。**worker 供给应与实际连接数/负载匹配**：
auto 模式总 worker 按 max_workers 封顶并按 Reactor 均摊，或按连接数动态收缩。

## 已知边界

- loopback 带宽封顶（~900MB/s）时聚合吞吐≈单连接，无法用下载吞吐验证
  扩展性；应改用 CPU 密集 RPS 基准（绕过带宽）。
- 测量环境噪声（同机高负载进程）使单次 5% 断言无法判定 → 配对对比
  （配置交替各 N 进程）是可靠下限。

## 验收信号

- 低并发下 rcN < rc1 不一定是 bug：先核查线程供给是否按 Reactor 放大、
  空闲线程是否超额，再归因实现缺陷。
