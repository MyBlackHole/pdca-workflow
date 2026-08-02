# T0199 事务级确定性交错验证：worker/discard/reclaim 并发交错矩阵

## 问题陈述

现有并发测试为端到端级（真实线程 + 真实时序：并发入队排空、RCU
读者写者），交错顺序不可控，无法保证覆盖 worker/discard/reclaim
事务边界的关键交错。loom crate 直接引入不可行：engine 使用
std::sync::{Mutex, Condvar}（engine.rs:16，7 处 Mutex + 3 处
Condvar）与 urcu Rcu/RcuThread（用户态 RCU，engine.rs:21），loom
只能建模自身 sync 原语，cfg 双实现会侵入生产代码且 RCU 无法建模
（RCU 读事务是并发核心）。改用引擎既有 FaultPoint 注入机制
（engine.rs:156-160）在事务边界做确定性交错注入。

## 目标

扩展 FaultPoint 到 worker/discard/reclaim 的事务边界（对齐上游
bch2_trans_begin 循环的"事务重启即交错点"语义），以确定性交错矩阵
验证并发正确性：写者×写者、写者×worker、RCU 读者×写者的交错注入下
操作成功/重试语义保留，最终一致性（verify_all + discard 队列 +
alloc/freespace 树）不破坏。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：事务重启=交错点（bch2_trans_begin
      循环、trans restart 语义）、worker 并发（discard.c fast_work
      循环与 max_discards_in_flight）、RCU 读者并发（bch2_trans 读者
      与写者），与 engine-local FaultPoint 机制（engine.rs:156-160、
      trans_maybe_inject_restart 注入点）对应。
- [ ] AC-2: FaultPoint 扩展：worker/discard/reclaim 事务边界新增
      确定性注入变体；注入下操作成功或重试（-12 重试）语义保留，
      无死锁/忙等（测试超时护栏 ≤1min）。
- [ ] AC-3: 并发交错矩阵：写者×写者（并发 queue/reclaim/allocate）、
      写者×worker（并发入队 + discard worker 交错注入）、RCU 读者×
      写者（读事务与写者交错）三类场景的确定性交错验证，最终
      verify_all + discard_queue_empty + 树一致。
- [ ] AC-4: 交错不变量：任意交错注入下 discard 队列最终排空（或
      EAGAIN 旋转后恢复）、alloc/freespace/need_discard 树与派生集
      一致（verify_bucket_indexes）、无桶泄漏（open_buckets 空）。
- [ ] AC-5: 库 API 行为不变（FaultPoint 枚举扩展为既有注入机制，
      枚举新变体默认不触发，生产逻辑零改动或最小化改动）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过
      一分钟。

## 实现决策

- 不引入 loom crate（std Mutex/Condvar + urcu 不可建模，侵入生产
  代码，违反零依赖/最小改动原则）；确定性交错用 FaultPoint 扩展 +
  屏障（Barrier）驱动。
- FaultPoint 新增变体（如 DiscardCommitRestart、ReclaimCommitRestart、
  WorkerPassRestart）：在 worker/discard/reclaim 事务提交前注入
  restart，对齐 trans_maybe_inject_restart 既有注入点
  （engine.rs:1445-1467 模式）。
- 交错矩阵测试：多线程（真实线程）+ Barrier 同步 + 注入计数控制，
  每场景确定性断言最终一致；proptest 生成注入位置序列（对齐
  既有模型测试风格）。
- 测试级检查点沿用 T0196 模式：交错后 verify_all + 队列/树断言。

## 范围外

loom/tokio 模型化调度器、生产代码并发原语替换、新增并发 API、
超线程/内存序证明。

## 备注

前置：T0196（worker 检查点模式）、T0197（模型裁决注入）、T0198
（fsck 修复）已归档；FaultPoint 既有 TransactionRestart /
JournalWrite 注入点（engine.rs:1445-1467）为扩展基线。
