# T0203 Triage Brief：并发组合序列（多写者 × alloc op × 崩溃恢复精确断言）

## 任务概述

组合 T0202（组合 op 域模型：btree × alloc 4 op × 崩溃恢复**精确**断言）
与 T0201（持久化并发：多线程写者 × 确定性崩溃点 abort）两个已验证模式：
**多写者线程**各自执行混合 op 序列，提交顺序由全局提交日志确定，
崩溃恢复后按 T0202 的三态模型做**精确**断言（非 T0201 的最终一致）。

T0201 用最终一致绕过交错不确定性；T0202 用单写者 + sync 点实现精确。
本任务的关键洞察：**子进程提交日志（锁序 append）= 精确性的确定性来源**
——崩溃点前各线程全部完成 + sync 落盘，模型 = 提交日志重放。

## 上游锚点（复用已核对结论，本次复核）

- journal replay 只回放已落盘事务（T0195/T0201 已验证）。
- 崩溃 = abort 不 flush（engine.rs:1801-1836），恢复 =
  replay + rebuild_derived_state（engine.rs:2014-2019）。
- alloc op 语义（allocate/reclaim/queue_discard/run_discard_worker_once）
  由 T0202 锚点表固定（foreground.c 候选规则、discard.c:643 darray、
  discover 重入队 engine.rs:1309）。
- 提交锁序：全局 fs 锁（T0199 并发矩阵已实测），提交日志顺序 = 锁序 =
  模型应用顺序。

## 方案

1. 子进程扩展 process_crash_child：新增组合模式——N(2-3) 个写者线程
   （Barrier 起跑，各自执行 combined op 序列：put/delete/allocate/
   reclaim/queue_discard/run_discard_worker_once），共享 engine；
   每次 op 成功后 append 提交日志（锁保护 Vec<OpRecord>）。
2. 崩溃点：全部线程完成 → 写提交日志文件 → sync（journal 落盘）→ abort。
3. 父进程：读提交日志重放 BucketModel（T0202 三态 + VecDeque 队列 +
   BTreeMap btree 模型），open_persistent 后精确断言（btree 内容 +
   alloc 树投影 + 队列/发现语义）。
4. 边界覆盖：并发空间耗尽（多写者 allocate 竞争 free 集）、重复
   queue_discard（-17 幂等语义在并发下）、worker 回旋。
5. 随机种子 + 确定性：seed 固定时提交日志内容确定（锁序下线程内部
   op 序列确定，交错仅影响相对顺序但日志捕获实际顺序）。

## 范围外

GC trigger、stripe/EC、open/close/set_rw 守卫域（T0197）、真实磁盘故障。
