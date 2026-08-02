# T0201 上游锚点记录（AC-1）

修改前逐段对照的本地 bcachefs-tools 源码与既有任务模式：

## 1. journal replay 只回放已落盘事务

journal 记录写盘后才可回放（replay 语义，T0195 已锚定）；未落盘
（unflushed）事务在崩溃时丢失。本项目 `bch2_journal_flush`
（journal.rs:995）写盘推进 seq 后记录才 durable。

→ 崩溃点=flush 前的场景，未落盘事务必须被丢弃（AC-3 实测）。

## 2. 后台 journal reclaim 周期回收

bcachefs journal_reclaim.c 的 workqueue 周期回收语义；本项目
`reclaim_worker_loop`（engine.rs:1855-1922）每 RECLAIM_WORKER_DELAY
（25ms）醒来，`request_reclaim_inner`（engine.rs:1764-1775）在
stopping 时拒绝新请求（Drop 语义：stopping=只读，对齐 bcachefs
ro 后拒新事务）。

→ 并发写者运行期间后台 reclaim 可能落盘部分记录，恢复存活集不确定
（cc-mid-write 只断言最终一致）；确定性丢弃场景必须排除后台落盘
（JournalWrite 注入，见下）。

## 3. 事务提交锁序（commit.c）

bch2_trans_commit → trans_maybe_inject_restart（commit.c:1390）→
journal res_get → 加锁 → verify_update_old_key → commit 写盘。
TransactionRestart 注入在提交入口消费（T0199 模式），共享计数被
并发写者消费。

## 4. 写盘失败不推进 seq

bch2_journal_flush 在构造记录与推进 seq 之前消费
fault_inject_write_error 并返回 -5（journal.rs:1009-1015）：失败后
journal 状态原样，内存记录保留。

→ JournalWrite 注入使任何 flush 尝试（含后台 reclaim）都失败，
abort 后内存记录必丢 → 恢复 0 键确定（T0196 故障矩阵既有机制）。

## 5. 既有模式复用

- T0195/T0196 崩溃子进程模式：run_crash_child / process_crash_child
  （engine.rs 既有），子进程 abort + 父进程 open_persistent 恢复。
- T0199 并发 Barrier 模式：Barrier 参与者数与 waiters 必须一致
  （4 写者 + 主线程 = Barrier(5)），主线程参与所有 barrier 保证
  轮次边界确定。
- 最终一致断言原则（T0199）：并发场景只断言最终一致，不依赖
  到达顺序或特定存活集。
