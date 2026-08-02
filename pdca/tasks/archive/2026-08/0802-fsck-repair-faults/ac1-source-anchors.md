# T0200 上游锚点记录（AC-1）

修改前逐段对照的本地 bcachefs-tools 源码：

## 1. 修复事务 restart 语义（-4）

上游 `__bch2_trans_commit` 在事务提交入口调用 `trans_maybe_inject_restart`
（fs/btree/commit.c:1390），返回 transaction_restart（-4）时走
out_reset 释放锁；`lockrestart_do`（fs/btree/iter.h:1115-1127）对
`bch2_err_matches(_ret2, BCH_ERR_transaction_restart)` **循环重试**
（do { bch2_trans_begin; ret = do; } while restart）。

→ 修复事务的 -4 必须重试而非中止。T0198 的 bit_mod_sync 只写了
`-12 && realloc_bytes_required != 0` 重试分支，缺 -4——本任务修复
为 `ret == -4 || (ret == -12 && ...)`，与引擎 reclaim_bucket
（engine.rs:1090）、allocate（engine.rs:886）既有模式一致。

## 2. 修复事务 ENOMEM 语义（-12）

- bch2_trans_commit -ENOMEM 且需要 realloc：事务内部扩容后返回
  -12，调用方重试（engine 既有条件 `ret == -12 && trans.realloc_bytes_required != 0`）。
- 真 OOM（restarted == 0 且无 realloc 需求）：走既有错误传播中止。

→ DuringRepairOom 注入 -12 且不满足 realloc 条件 → 走 `bch2_trans_put`
+ `Err(Transaction(-12))` 中止修复，零新分支。

## 3. 修复事务形态

`delete_freespace_key`（fs/alloc/check.c:366-371）：每键一事务
`bch2_trans_commit(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc)`，
失败返回错误中止（`try()` 宏，fs/util/util.h:831-838）。

→ bit_mod_sync 每键单事务、失败传播错误，对齐。

## 4. 落盘失败传播

fs.exit()（fs/fs/fsck.rs:457-460）失败 → fsck 返回错误，不发布成功。

→ AfterRepairBeforeFlush 在 flush_journal 前返回 Journal(-5)，修复
虽已提交但未落盘，不误报成功；重跑时 journal replay 只回放已落盘
事务（T0195 验证语义），未落盘修复被丢弃，重跑修复收敛。

## 5. 故障矩阵模式（复用既有）

- RecoveryFaultPoint 一次性注入（engine.rs:166-171，消费于
  recover_with_fault）+ recovery_fault_matrix_never_publishes_success
  断言（engine.rs:4323-4343）。
- FaultPoint/一次性计数注入先例（T0199）。

→ FsckFaultPoint 对齐同一模式：一次性消费（&mut Option，首个修复
事务吞掉），矩阵测试遍历失败注入点断言 Err。
