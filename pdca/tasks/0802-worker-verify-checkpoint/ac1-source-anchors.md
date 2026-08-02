# T0196 AC-1 上游锚点记录

## 上游 discard worker 循环

`fs/alloc/discard.c:598-633` `bch2_do_discards_fast_work`：

```
598  void bch2_do_discards_fast_work(struct work_struct *work)
600    struct bch_dev *ca = container_of(work, struct bch_dev, discard_fast_work);
...
608      while (1) {
...
626        } while (ret == -BCH_ERR_max_discards_in_flight);
633      event_inc_trace(c, bucket_discard_fast_worker, buf, ({ ... }))
```

- fast_work 循环逐桶 discard；`max_discards_in_flight` 边界内重试
  （626 行 `ret == -BCH_ERR_max_discards_in_flight` 循环）。
- engine-local 对应：`run_discard_worker`（engine.rs:1216，FIFO pass、
  EAGAIN 旋转到队尾、terminal error 中止，discard.c:488-491/631-633
  锚点已记录于 T0190）、`run_discard_worker_once`（engine.rs:1171）。

## 上游 journal reclaim

`fs/journal/reclaim.c`（bch2_journal_reclaim 系列：journal 空间低水位
触发 checkpoint 回收，驱动 journal seq 推进与 btree 写回）。
engine-local 对应：`request_reclaim`（engine.rs:1337，唤醒
reclaim_worker_loop）、`reclaim_worker_loop`（engine.rs:1814，
RECLAIM_WORKER_DELAY 定时 + wake 唤醒，state.requested/completed 记账）、
`reclaim_background_once`（engine.rs:1740，seq_ondisk 推进时
checkpoint_locked）。

## 上游 worker 维护状态与 fsck 校验的验证关系

`fs/alloc/check.c:323-345`：

```
323  struct check_freespace_key_async {
...
329  static int bch2_recheck_freespace_key(struct btree_trans *trans, struct bbpos pos)
336      ? __bch2_check_freespace_key(trans, &iter, &gen, NULL, FSCK_ERR_SILENT, NULL)
342    struct check_freespace_key_async *w =
343      container_of(work, struct check_freespace_key_async, work);
345    bch2_trans_do(w->c, bch2_recheck_freespace_key(trans, w->pos));
```

- fsck 通过 `check_freespace_key` 校验 freespace 与 alloc 一致性——
  worker 写出的 freespace/need_discard 派生状态可被一致性校验验证。
- engine-local 对应：`verify_bucket_indexes`（verify_all 内部，T0194
  聚合：alloc vs freespace/need_discard 双向核对）。

## engine-local 既有检查点 API（无需新增）

- `verify_all`（engine.rs:739）：拓扑→派生状态→桶索引→守卫，首错优先。
- `discard_queue_empty`（T0193 公开断言）：queue 空不变量。
- `verify_guard_invariants`（T0193 公开断言）：守卫状态。

## 结论

worker 维护的派生状态与一致性校验的关系上游可证（discard.c 循环 →
freespace 由 fsck 校验）；测试级检查点（run 后 verify_all +
discard_queue_empty）不引入上游不存在的行为，库 API 保持不变。
