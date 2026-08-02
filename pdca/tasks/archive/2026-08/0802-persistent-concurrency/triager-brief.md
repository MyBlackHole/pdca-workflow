# T0201 Triage Brief：持久化并发交错

## 任务概述

组合 T0199（并发交错注入）与 T0195/T0196（崩溃恢复矩阵）两个
已验证模式：子进程内并发写者 + 确定性崩溃点 abort，父进程恢复后
验证最终一致。验证 bcachefs 事务一致性核心承诺——崩溃发生在并发
任意时刻，恢复后不变量成立。

## 上游锚点（已核对）

- journal replay 只回放已落盘事务（journal replay 语义，T0195 已
  验证 process_abort_recovery_observes_only_durable_boundaries，
  engine.rs:5030-5044）。
- open_persistent 恢复 = replay + rebuild_derived_state（清 4/5/8
  树重建派生态，engine.rs:2014-2019）。
- 引擎 Drop 不 flush（engine.rs:1801-1836 只停 worker + open 桶
  泄漏断言），abort 崩溃与真实 crash 语义一致。
- 并发提交锁序（全局 fs 锁），T0199 并发矩阵已实测最终一致。

## 方案

1. 子进程扩展：process_crash_child 增加并发模式——N 线程写者
   （allocate/reclaim/queue/discard worker 混合）Barrier 起跑 +
   TransactionRestart 注入；主线程按崩溃点 abort：
   - flush-before：写者提交部分事务后（未 flush）abort → 恢复须
     丢弃未落盘事务
   - flush-after：flush_journal 后 abort → 全部存活
   - mid-write：写者运行中（未完成）abort → 恢复后 verify 通过
2. 父进程断言：open_persistent + verify_all + open_bucket_count==0
   + scan 完整；只依赖最终一致。
3. 崩溃点同步：沿用 ready 文件机制（写 ready = 到达可崩溃点）。

## 风险

- 子进程并发写者线程在 abort 前可能持有锁——abort 直接终止进程，
  锁不释放无碍（进程退出内核回收）；父进程新开引擎不受影响。
- 崩溃点=flush-before 时"部分落盘"的确定性：并发写者各自提交
  事务（commit 即入 journal buffer），flush 前 abort → 只有已 flush
  的事务落盘。断言只依赖 verify_all（不依赖具体键值）。
- 超时控制：子进程并发写有界（有限轮次），父进程测试总时长
  需 ≤1min（AC-6）。

## 建议

按上述方案立项；AC-1 锚点、AC-2 并发崩溃子进程、AC-3 恢复矩阵、
AC-4 注入组合、AC-5 零生产改动、AC-6 门禁。
