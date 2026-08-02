# T0199 结论

## 概述

事务级确定性交错验证：loom crate 直接引入不可行（engine 用
std::sync::{Mutex, Condvar} 与 urcu Rcu，loom 只能建模自身原语，
cfg 双实现侵入生产代码），改用既有 FaultPoint 注入机制在
worker/discard/reclaim 事务边界做确定性交错。

实现（subvol `b3a5f64`，2 files +202/-3）：
- FaultPoint::DiscardCommitRestart：reclaim_bucket 每桶事务提交前
  注入 -4 重启（对齐 commit.c:1390 trans_maybe_inject_restart 位置、
  bch2_discard_one_bucket 每桶一事务 discard.c:289），-4 走既有
  bch2_trans_begin 重试循环，**零新逻辑分支**（约束 12）。
- fault_inject_discard_restarts 独立计数（btree/types.rs:505-510，
  对齐 fault_inject_transaction_restarts 形态）：只注入 discard 路径。
- 4 个交错矩阵测试：单线程注入排空（6 次注入×4 桶）、写者×写者
  （4 线程 Barrier + 12 次 TransactionRestart）、写者×worker
  （生产者并发入队 + worker 排空 + DiscardCommitRestart）、RCU
  读者×写者（24 次注入）；断言只依赖最终一致（triager round 2
  口径）。

## 验证

- 239 全绿（224 lib + 10 btree_proptest + 5 fsck_cli），单项
  ≤1min（proptest 39.61s）；fmt 通过。
- 生产逻辑零行为改动（既有 220 lib 无回归）；双轴审查
  0 blocking / 0 MEDIUM / 0 LOW。
- 注入点并发安全：fetch_update(AcqRel/Acquire) 原子共享计数。

## 排查记录（全部为测试构造问题，非引擎缺陷）

1. **持久化几何固定 8 桶**（8MB 文件 / 1MB 桶，JOURNAL_BUCKET_SIZE
   =2048 sectors，engine.rs:81/2670）：create_persistent 截断文件，
   set_len 无法扩大；桶 4..=7 之外 add_free_bucket 建的键越界
   （allocate 按 nbuckets 检查正确跳过）。修复：4 桶循环复用（二次
   reclaim NEED_DISCARD→FREE + freespace 补键 engine.rs:1043-1049，
   或 discard 归还）。
2. **queue_discard_bucket 断言副作用入队**：FREE 桶触发 discard_bucket
   前置 -11 检查（1106-1149 要求 NEED_DISCARD）→ run_discard_worker
   按 EAGAIN 语义无限旋转（对齐 discard.c:488-491）。修复：队列长度
   断言（读 discard_inflight）。
3. **Barrier 参与者数**：Barrier(5) = 4 生产者 + 主线程 wait；缺 1
   参与者则主线程永久阻塞。

## 建议链（下一轮）

1. 模型状态机扩展：op 域扩大（含并发语义的 op 序列）、case 数提升
   （T0197 模型的 op 集仍为顺序模型；并发矩阵已由 T0199 覆盖）。
2. fsck 修复的故障注入：修复事务中途 -12/-ENOMEM 注入与恢复路径
   （T0198 修复路径 + T0196 recovery-fault-matrix 模式）。
3. 持久化并发：并发写者 + checkpoint/reclaim 交错下的 journal
   落盘与 reopen 一致性（T0199 矩阵 + open_persistent 组合）。
