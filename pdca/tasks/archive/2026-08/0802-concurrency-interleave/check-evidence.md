# T0199 Check Evidence（事务级确定性交错验证）

## 验证环境

- subvol commit `b3a5f64`（2 files +202/-3：engine.rs、btree/types.rs）
- workspace 全量：224 lib + 10 btree_proptest + 5 fsck_cli = 239 全绿
- 单项耗时：lib 10.32s、proptest 39.61s、fsck_cli 0.04s（约束 9 ✓）
- cargo fmt 通过

## AC-1 锚点记录（audit，ac1-source-anchors）

ac1-source-anchors.md 逐段对照并记录：事务重启=交错点
（iter.h → iter.rs:662-684 返回 -4、commit.c:1390 注入位置）；
discard worker fast_work 每桶一事务（discard.c:598-657/289/488/
622）；并发入队 bch2_fast_discard_bucket_add（discard.c:643）；
reclaim worker journal 水位（reclaim.c → checkpoint_locked）；
RCU 读者×写者。✓

## AC-2 FaultPoint 扩展（traceability，E-0001）

- `DiscardCommitRestart` 变体（engine.rs:160-163）+ 独立计数
  `fault_inject_discard_restarts`（btree/types.rs:505-510，对齐
  fault_inject_transaction_restarts 形态）。
- 注入点 = reclaim_bucket 每桶事务提交前（engine.rs:1081-1095）：
  命中返回 -4，走既有 `ret == -4` continue 重试（1096-1100），
  **零新逻辑分支**（约束 12）；注入路径全部复用上游 restart 语义。
- 无死锁/忙等：注入点位于事务提交前（无锁段外——fs 锁持有但无
  等待其他锁），测试超时护栏 1min 全绿。✓

## AC-3 并发交错矩阵（traceability，E-0001）

| 场景 | 测试 | 注入 | 断言 |
|---|---|---|---|
| 单线程 worker 注入 | discard_commit_restart_injected_worker_retries_and_drains | DiscardCommitRestart×6 | 队列空、桶 freed、verify_all |
| 写者×写者 | concurrent_writers_with_restart_injection_converge | TransactionRestart×12 | 4线程×6轮全成功、verify_all、无泄漏 |
| 写者×worker | concurrent_producers_and_discard_worker_with_injection_drain | DiscardCommitRestart×2/轮 | 队列最终空、3轮循环、verify_all |
| RCU 读者×写者 | rcu_readers_with_writer_restart_injection_keep_order | TransactionRestart×24 | 每次 scan 有序、96 键、verify |

全部 4 个测试通过（0.12s 合集）。✓

## AC-4 交错不变量（traceability，E-0001）

- 队列最终排空：生产者×worker 3 轮后队列长度 0 断言
  （discard_inflight 直接读取，避免 queue 副作用）。
- 树一致：每场景 verify_all（含 verify_bucket_indexes 派生集检查）。
- 无桶泄漏：Drop 断言 open_buckets 空（engine.rs:1788-1793）+ 写者
  测试显式 drop。✓

## AC-5 API 行为不变（code-review，E-0002）

- 生产逻辑零行为改动：仅 FaultPoint 枚举新变体 + inject_fault 分支
  + 一个提交前注入点；既有 220 lib 测试全绿无回归（含 T0196/T0197
  注入测试 2847/3000/3557 等）。
- 新变体默认不触发（计数 0，fetch_update 不命中）；API 签名不变。✓

## AC-6 全量门禁（code-review，E-0002）

- 224 lib + 10 proptest + 5 fsck_cli 全绿；fmt clean；单项 ≤1min。✓

## 排查记录（测试构造问题，非引擎缺陷）

1. 持久化几何固定 8 桶（8MB 文件 / 1MB 桶，JOURNAL_BUCKET_SIZE
   =2048 sectors，engine.rs:81/2670）：set_len 无法扩大（attach 截断），
   桶 4..=7 之外 add_free_bucket 建的键越界（allocate 按 nbuckets
   检查正确跳过，对齐成员几何语义）。修复：4 桶循环复用（二次
   reclaim NEED_DISCARD→FREE + freespace 补键，engine.rs:1043-1049；
   或 discard 归还）。
2. queue_discard_bucket 断言副作用入队：FREE 桶触发 discard_bucket
   前置检查 -11（1106-1149 要求 NEED_DISCARD）→ worker 无限旋转
   （EAGAIN 语义，对齐 discard.c:488-491 旋转）。修复：改队列长度
   断言。
3. Barrier 参与者数：Barrier(5) = 4 生产者 + 主线程 wait，缺 1 则
   主线程永久阻塞（writers 测试 Barrier(4) 无主线程 wait 正确）。
