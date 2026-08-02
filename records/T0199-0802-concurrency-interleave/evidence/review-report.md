# T0199 Review Report（双轴审查）

## 审查范围

subvol `b3a5f64` diff（engine.rs +202/-3、btree/types.rs +4）：
FaultPoint::DiscardCommitRestart、fault_inject_discard_restarts、
reclaim_bucket 注入点、4 个交错矩阵测试、prepared_bucket_engine
重构（拆分 32MB 常量参数，后回退）。

## 轴 1：上游语义对齐（对照本地 bcachefs-tools）

| 项 | 结论 |
|---|---|
| 注入位置 | reclaim_bucket 事务提交前 = bch2_discard_one_bucket（discard.c:289）内 commit.c:1390 trans_maybe_inject_restart 位置 ✓ |
| 重启语义 | 返回 -4（iter.rs:679-683 既有协议）+ 既有 continue 重试（-4 或 -12 条件，engine.rs:1096-1100）✓ 零新分支 |
| 每桶一事务 | run_discard_worker → discard_bucket → reclaim_bucket 单事务（1030-1091）= fast_work 逐桶 trans（discard.c:598-657）✓ |
| EAGAIN 旋转 | worker -11 旋转 = fastpath advance-and-continue（discard.c:488-491）✓（排查记录 2 依赖此语义） |
| 入队去重 | queue_discard_bucket -17 = discard_in_flight_add EEXIST（discard.c:124-128）✓ |
| 几何 | nbuckets=8 = members 几何（engine.rs:2670 对齐 bch_member）✓ |

## 轴 2：Rust 正确性审查

### Blocker（0）
无。

### Medium（0）
无。

### Low（0）
无。

## 风险评估

- 并发测试的确定性：断言只依赖最终一致（上游并发语义本身不保证
  到达顺序）；Barrier + 注入计数提供交错机会但非全序 —— 与 triager
  grilling round 2 口径一致（已记录 clarifications.jsonl）。
- 注入点并发安全：fetch_update(AcqRel/Acquire) 原子，跨线程共享
  消费计数；无锁内等待（fs Mutex 持有但注入仅原子 decrement）。
- 回归风险：生产路径零行为改动，既有 220 lib 测试全绿验证。

## 结论

0 Blocker / 0 Medium / 0 Low，可进入 check 阶段。
