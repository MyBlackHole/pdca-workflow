# T0199 Triage Brief：事务级确定性交错验证

## 任务概述

建议链提出"loom 风格并发交错：worker/discard/reclaim 在并发下的
事务级验证（现有并发测试为端到端级）"。经调研，**直接引入 loom
crate 不可行**，本任务改为引擎既有 FaultPoint 注入机制的确定性
交错扩展。

## 不可行性论证（loom 直接引入）

| 项 | 事实 | 结论 |
|---|---|---|
| 同步原语 | engine 使用 std::sync::{Mutex, Condvar}（engine.rs:16，Mutex 7 处 + Condvar 3 处） | loom 只建模自身 sync 原语，std 原语触发 panic |
| RCU | urcu Rcu/RcuThread（engine.rs:21），RCU 读事务是并发核心 | loom 无法建模外部真实 RCU 实现 |
| 改造成本 | cfg 双实现需改动生产代码全部锁点 + 原子 + urcu 交互 | 侵入生产代码，违反零依赖/最小改动 |
| 替代 | FaultPoint 既有注入机制（engine.rs:156-160，TransactionRestart/JournalWrite，对应 trans_maybe_inject_restart 语义） | 零生产逻辑改动，仅枚举扩展 + 测试 |

## 上游锚点（已核对）

- 事务重启=交错点：`trans_maybe_inject_restart`（fs/btree/commit.c:1390、
  iter.c:2936/3192/3344/3769），bch2_trans_do 循环天然支持交错——
  engine 的 `trans_maybe_inject_restart()` 注入点（engine.rs:1445-1467）
  即对应实现，TransactionRestart 故障注入下操作通过重试成功
  （engine.rs:2847/3000/3557 既有测试证明）。
- discard worker 并发：`bch2_do_discards_fast_work`（fs/alloc/discard.c:598-
  657）每次出桶调 `bch2_discard_one_bucket`（289，488/622 调用）——每桶
  一事务一提交，事务边界即交错点；`in_flight` 队列（102-132，
  max_discards_in_flight 128 限制）→ engine `discard_inflight` 队列
  （engine.rs:436）。
- worker 并发：engine ReclaimWorker（engine.rs:411-413 state+wake，
  Mutex+Condvar）对应上游 write_ref_wq。

## 方案

1. FaultPoint 扩展：新增 `DiscardCommitRestart` / `ReclaimCommitRestart`
   （worker/discard 事务提交前注入 restart，对齐 trans_maybe_inject_
   restart 注入点位置）。
2. 交错矩阵（真实线程 + Barrier + 注入计数，确定性）：
   - 写者×写者：并发 queue/reclaim/allocate 交替 + 随机注入点
   - 写者×worker：并发入队 + discard worker 每桶注入 restart
   - RCU 读者×写者：读事务遍历与写者事务交错注入
3. 断言：每场景 verify_all + discard 队列最终排空 + 树一致 +
   open_buckets 空（沿用 T0196 检查点模式）；proptest 生成注入序列。
4. 超时护栏：单项 ≤1min（约束 9）。

## 风险

- 确定性保持：真实线程 + 注入计数下交错非全序可控，断言仅依赖
  最终一致（对齐上游：并发下只保证最终一致，不保证到达顺序）。
- worker 停顿注入点若在持锁段内会死锁 → 注入点仅限事务提交前
  （无锁段），测试断言 + 超时护栏兜底。

## 建议

按上述方案立项（FaultPoint 扩展 + 交错矩阵），生产逻辑零改动或
最小化；AC-1 锚点记录、AC-2 注入扩展、AC-3 矩阵、AC-4 不变量、
AC-5 API 不变、AC-6 全绿。
