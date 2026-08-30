---
schema: pdca.asset/v1
id: ontology:domain/core-deterministic-interleave
type: domain
layer: Knowledge
status: active
summary: 事务级确定性交错模式（Deterministic Interleave）
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 事务级确定性交错模式（Deterministic Interleave）

## 适用场景

需要验证并发正确性但交错不可控（真实线程时序）时：在**事务边界**
注入确定性重启/停顿，断言只依赖**最终一致**（上游并发语义只保证
最终一致，不保证到达顺序——避免 flaky）。

## 模式要点

1. **loom 类模型调度器不可用时的替代**：loom 只能建模自身 sync
   原语；std::sync::{Mutex, Condvar}、外部真实 RCU（urcu）无法建模，
   cfg 双实现侵入生产代码。**改用既有故障注入点 + 真实线程 +
   Barrier**：注入点制造重启窗口，Barrier 同步起跑，原子计数
   （fetch_update AcqRel decrement）跨线程共享消费——谁先到谁被
   注入，交错非全序但断言不依赖顺序。
2. **注入点必须在事务提交前**（trans_maybe_inject_restart 位置，
   commit.c:1390）：命中返回 -4，走既有 `-4 || -12` continue 重试
   循环（bch2_trans_begin 重置事务）——**零新逻辑分支**，注入语义
   全部复用上游 restart 协议。绝不在持锁等待段注入（死锁）。
3. **按路径独立计数**：通用计数（fault_inject_transaction_restarts）
   会被任何事务消费；需要只注入特定路径（如 discard worker）时用
   独立计数（fault_inject_discard_restarts），测试不扰动用户事务。
4. **并发测试的断言设计**：join 后断言最终状态（verify_all/队列
   空/无泄漏/有序），不在运行中做顺序断言；超时护栏 1min。
5. **测试几何陷阱**：持久化引擎几何固定（8MB/1MB 桶 = 8 桶，
   nbuckets 来自文件大小，attach 会截断文件——set_len 无效）；建
   桶须在 [first_bucket, nbuckets) 内，越界键会被 allocate 按
   nbuckets 检查正确跳过（ENOSPC -28 的隐蔽来源）。桶循环复用：
   二次 reclaim（NEED_DISCARD→FREE + freespace 补键）或 discard
   归还 freespace。
6. **EAGAIN 旋转陷阱**：run_discard_worker 对不满足前置条件的桶
   无限旋转（对齐 discard.c:488-491 语义）——测试断言不要把入队
   当无副作用操作（queue_discard_bucket 真实入队），验证排空用
   队列长度断言。

## 并发矩阵（本实现确认）

- 写者×写者：多线程 allocate/reclaim 争用全局锁 + 共享注入计数。
- 写者×worker：生产者并发入队 + worker 排空 + 注入。
- RCU 读者×写者：读者（RCU guard，不持锁）与写者并发，注入写者
  事务；每次 scan 有序 = 读一致快照。
- Barrier 参与者数必须与 wait 数一致（Barrier(n) 只放行 n 次，
  主线程 wait 也是参与者）。
