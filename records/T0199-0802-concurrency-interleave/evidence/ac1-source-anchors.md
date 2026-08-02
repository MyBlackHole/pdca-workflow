# T0199 AC-1 上游锚点记录（并发交错语义）

逐段对照本地 bcachefs-tools 源码与 engine-local 对应实现，确认
"事务重启即交错点"语义与注入位置。

## 1. 事务重启 = 交错点（trans_maybe_inject_restart）

- 上游 `trans_maybe_inject_restart()`（fs/btree/iter.h）：在事务
  提交路径被调用，返回 -EINTR 类重启错误；`bch2_trans_do` /
  `bch2_trans_begin` 循环负责回滚重试，**一次 restart 就是一次
  事务交错点**。注入位置（提交前、副作用前）：
  - fs/btree/commit.c:1390（bch2_btree_trans_commit 内）
  - fs/btree/iter.c:2936/3192/3344/3769（迭代重取路径）
- 移植实现：iter.rs:662-684 `bch2_trans_maybe_inject_restart`：
  `fault_inject_transaction_restarts` 计数 fetch_update（AcqRel
  decrement），命中返回 -4（BCH_ERR_transaction_restart_fault_
  inject），`trans->restarted = 4`；调用点 update.rs:2848-2851
  （commit.c:1390 对应，提交前）。计数为 AtomicU32，跨线程共享
  消费 → 多线程注入天然支持。
- 重试语义：engine 事务循环统一 `if ret == -4 || (ret == -12 &&
  realloc_bytes_required != 0) { continue; }`（engine.rs:1086、
  add_free_bucket 3157、T0196/T0197 同型）。

## 2. discard worker = fast_work（每桶一事务）

- 上游 `bch2_do_discards_fast_work`（fs/alloc/discard.c:598-657）：
  while 循环（605-633）逐桶出队，每次调 `bch2_discard_one_bucket`
  （488/622），**每桶新建 btree_trans + 提交**（天然的交错点）；
  EAGAIN 旋转（488-491），终端错误 break（631-633）；
  in_flight 去重（102-132，EEXIST 边界 124-128）对应 engine
  discard_inflight 集合（engine.rs:436）。
- 移植：`run_discard_worker`（engine.rs:1216-1267）逐桶循环调
  `discard_bucket`（1106-1151）→ `reclaim_bucket`（955-1098）
  内 1030-1091 每桶单事务（bch2_trans_begin/commit 循环）。
- 并发入队：`bch2_fast_discard_bucket_add`（discard.c:643，FIFO
  darray）对应 `queue_discard_bucket`（engine.rs:1157-1168）。

## 3. reclaim worker = journal reclaim 线程

- 上游 reclaim.c：journal flush + flush_pins + last_seq 推进的
  后台线程（write_ref_wq）；engine `reclaim_worker_loop`
  （engine.rs:1814-1880）经 `background_reclaim_needed`（1882-
  1890）判断 journal 水位，`reclaim_background_once`（1749-1757）
  → `checkpoint_locked`（1479+）。reclaim 无 btree 事务，交错点
  为 journal flush（JournalWrite 注入已有，engine.rs:1467-1470）。

## 4. RCU 读者 × 写者

- 上游：bch2_trans 读事务经 RCU/锁保护与写者并发；写者提交
  不阻塞读者迭代（读迭代拿一致快照）。
- 移植：`read_transaction()`（rcu read guard）与写者事务并发，
  既有端到端测试 concurrent_rcu_read_transactions_and_writers_
  keep_iterator_order（engine.rs:4562-4603）。

## 5. 注入点设计结论（对齐语义）

- 新变体 `DiscardCommitRestart` 的注入位置 = reclaim_bucket 事务
  提交前（engine.rs:1081-1085 的 bch2_trans_commit 调用点），即
  discard.c 每桶事务的 commit.c:1390 对应位置；返回 -4 走既有
  continue 重试（1086），**零新逻辑分支**（对齐约束 12：注入
  路径全部复用上游 restart 语义）。
- 独立计数 `fault_inject_discard_restarts`（对齐
  fault_inject_transaction_restarts 形态，btree/types.rs:505），
  使测试可只注入 discard 路径而不影响用户事务。
