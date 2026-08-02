# T0191 AC-1 源码锚点（修改前记录）

对照基准：`/home/black/Documents/bcachefs-tools/fs/alloc/discard.c`

## 1. 遍历（主路径，按 journal_seq 排序）

`bch2_do_discards`（discard.c:455-557）：

- `for_each_btree_key(trans, iter, BTREE_ID_need_discard, POS_MIN, 0, ...)`
  （discard.c:468）：从 POS_MIN 起遍历 need_discard btree，键序按
  `journal_seq`（`k.k->p.inode`）+ bucket（`k.k->p.offset`）确定，即
  **先标记的桶先遍历**。
- 遍历终止条件：`journal_seq >= min(rewind_seq_ondisk, flushed_seq_ondisk + 1)`
  （discard.c:478）时 break —— 只处理 journal 边界已落盘的桶。

## 2. 重试（EAGAIN / -max_discards_in_flight）

- `bch2_discard_one_bucket`（discard.c:289）：单桶 discard 提交；
  返回 `-BCH_ERR_max_discards_in_flight` 表示设备 in-flight 并发已达上限。
- 主路径（discard.c:483-495）：`ret2 == -max_discards_in_flight` 时不 advance，
  调用 `bch2_discards_complete` 后由外层重试该桶；成功且
  `in_flight.nr > ref` 时 `bch2_btree_iter_advance`（discard.c:489）**跳过继续
  遍历后续桶** —— 单桶未完成不阻塞其他桶。
- fastpath（discard.c:617-621）：`do { ... } while (ret == -max_discards_in_flight)`
  同一桶 do-while 重试直到成功。

## 3. going-ro 边界

`bch2_do_discards_going_ro`（discard.c:560-577）：遍历 rw member，
仅当 `free < stripe_watermark * 4` 且存在 need_discard 桶时才执行
`bch2_do_discards`；否则跳过。

## 4. fastpath（per-device FIFO + 单 worker 耗尽循环）

- `bch2_fast_discard_bucket_add`（discard.c:643-661）：
  `scoped_guard(mutex, &ca->discard_fast_lock) darray_push(&ca->discard_fast, bucket)`
  —— **提交顺序 = 入队顺序（darray FIFO）**；重复提交不查重（上游语义），
  由 write_ref tryget 保证同一时间单 worker 执行。
- `bch2_do_discards_fast_work`（discard.c:598-641）：
  `scoped_guard(mutex) bucket = darray_pop(...)`（discard.c:607-610）；
  `while (1) { ... if (!bucket) break; ... }`（discard.c:605-633）——
  单 worker 循环 pop 处理**直到队列耗尽**，每桶处理完 `bch2_discards_complete`
  收束；出错 break。

## 5. engine-local 现状（T0190 基线）

`crates/subvol/src/engine.rs`：

- `discard_inflight: Mutex<BTreeSet<(u64, u64)>>`（engine.rs:434）：单集合做
  in-flight 去重；`run_discard_worker_once` 取 `.iter().next()`（engine.rs:949）
  字典序首项 —— **无提交顺序语义**。
- `queue_discard_bucket`（engine.rs:927）：BTreeSet insert 失败返回
  EEXIST(-17)。
- `discard_bucket`（engine.rs:896）：bucket 未标记 need_discard 或
  `journal_seq_empty > last_seq_ondisk` 返回 EAGAIN(-11)。
- `discover_discard_buckets`（engine.rs:970）：重启后从 need_discard btree
  重新发现并入队（按 btree 扫描序）。

## T0191 映射结论

- FIFO 顺序 ← discard.c:643-655 darray_push 提交序 / discard.c:607-610 pop。
- while 直到耗尽 ← discard.c:605-633 fast_work 主循环。
- EAGAIN 移队尾轮转（不阻塞其他桶）← discard.c:488-491 advance 跳过继续
  遍历语义（engine-local EAGAIN ≠ 上游 max_discards_in_flight，不可重试同一桶）。
- going-ro 与 write_ref 并发闸门在 engine-local 由 Mutex 单 worker 对应。
