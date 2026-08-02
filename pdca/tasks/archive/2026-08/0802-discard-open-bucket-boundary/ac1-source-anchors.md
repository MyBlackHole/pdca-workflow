# T0189 AC-1 源码锚点 — discard 边界与 open-bucket 回收保护

修改前逐段记录，与本地 bcachefs 源码对照（约束 10）。

## 1. `__discard_mark_free` — 转 free 的唯一合法路径

`fs/alloc/discard.c:163-219`：

- `a->v.data_type != BCH_DATA_need_discard` → 打印 + `bch2_fs_emergency_read_only`
  （丢弃了非 need_discard 桶是致命错误，emergency RO）。
- 转 free 的同一更新内清空三处簿记：`SET_BCH_ALLOC_V4_NEED_DISCARD(false)`、
  `data_type = BCH_DATA_free`、`journal_seq_nonempty = 0`、`journal_seq_empty = 0`；
  `alloc_data_type_set` 同步类型位（discard.c:186-191）。
- `bch2_trans_update(iter, ..., BTREE_TRIGGER_is_discard)` + 同事务
  `bch2_trans_commit`（discard.c:193-203）；commit 失败传播错误。

engine-local 对应：`reclaim_bucket`（engine.rs:762）第二次调用（桶已在
need_discard）同事务更新 alloc 值 + FREESPACE bit on + NEED_DISCARD bit off；
`discard_bucket`（engine.rs:896）为受控边界。现有实现已同事务（AC-3 基线）。

## 2. open bucket 保护 — 转 free 前置条件之一

`fs/alloc/foreground.h:274-296`：

- `bch2_bucket_is_open()`：在 `allocator.open_buckets` 哈希中按 (dev, bucket)
  查找；`bch2_bucket_is_open_safe()` 加 freelist_lock 保护后重查。
- open bucket = 正在被写入的 bucket（有 write point 引用）。

`fs/alloc/discard.c:344-347`（`bch2_discard_one_bucket`）：

```c
/* Must check after we've looked at and locked the alloc key: */
if (bch2_bucket_is_open_safe(c, bucket.inode, bucket.offset)) {
    s->open += bucket_size;
    return 0;   /* 跳过，不计错误 */
}
```

`fs/alloc/discard.c:433-436`（`bch2_do_discards` need_discard 遍历）：

```c
if (bch2_bucket_is_open_safe(c, bucket.inode, bucket.offset))
    continue;
```

`fs/alloc/discard.c:743`（`bch2_discard_bucket` 直接路径）同样先查 open。

`fs/alloc/background.c:1270-1277`：非空→空转换时 WARN「bucket going empty
but not open」；`background.c:1301-1306`：离开 need_discard 到非空必须
open（`WARN_ON(!bch2_bucket_is_open_safe(...))`）。

engine-local 现状：**无 open bucket 概念**（engine.rs 无 open_buckets 结构）。
`reclaim_bucket` 仅检查 backpointer 无 live 条目 + dirty/cached_sectors==0。
缺口确认：分配后"写入进行中"的桶可被直接回收。

## 3. journal boundary — 转 free 前置条件之二

`fs/alloc/discard.c:320-339`（`bch2_discard_one_bucket`）：

- `a->v.journal_seq_empty` 非零（fastpath 误入）→ `need_journal_commit`。
- `journal_seq_empty > flushed_seq_ondisk` → `need_journal_commit`（journal
  未落盘，跳过）。
- `journal_seq_empty >= rewind_seq_ondisk` → `need_rewind_advance`（跳过）。
- `data_type != BCH_DATA_need_discard` → `bad_data_type`（预期竞态，跳过）。

engine-local 对应：`discard_bucket`（engine.rs:916）与 `reclaim_bucket`
（engine.rs:804）检查 `journal_seq_empty > last_seq_ondisk` → -11（EAGAIN
seam，T0190 定），已存在。AC-2 基线部分满足。

## 4. 设备可写 — 转 free 前置条件之三

`fs/alloc/discard.c:357-365`：

```c
struct bch_dev *ca = bch2_dev_get_ioref(trans->c, bucket.inode, WRITE,
                        BCH_DEV_WRITE_REF_discard_bucket);
if (!ca) {
    s->not_rw += bucket_size;
    return 0;   /* 设备不可写，跳过 */
}
```

`fs/alloc/background.c:1650-1667`：`bch2_dev_allocator_set_rw()` 维护
`allocator.rw_devs` bitmap（data_allowed 与 durability 联合决定）；
`background.c:1694` 设备下线时清 rw。

engine-local 现状：**无 rw 状态**。allocate_bucket 检查 `bch2_member_alive`
（engine.rs:693）但不检查 rw；discard/reclaim 不检查设备可写。缺口确认。

## 5. 重试分支 — 遍历/提交/重试

`fs/alloc/discard.c:429-557`（`bch2_do_discards`）：

- 按 need_discard btree（按 journal_seq 排序）遍历；`journal_seq >=
  min(rewind_seq_ondisk, flushed_seq_ondisk+1)` 停止（discard.c:456-458）。
- 每个桶 `bch2_discard_one_bucket`；`-max_discards_in_flight` 或成功后
  advance 并 `bch2_discards_complete`（discard.c:480-495）。
- 每轮后：`calculate_discard_sectors_to_release`（rewind 预算，
  discard.c:382-427）；`bch2_journal_advance_rewind_seq`；flush_journal /
  flush_wb 触发 `again=true` 重跑；`while (!ret && again)`（discard.c:549）。

engine-local 对应：T0190/T0191 已建 `queue_discard_bucket`（EEXIST，
engine.rs:929）、`run_discard_worker_once`（engine.rs:943）、
`run_discard_worker`（while-耗尽，engine.rs:988）、`discover_discard_buckets`
（engine.rs:1043）。fastpath darray FIFO = engine-local VecDeque。

## 映射结论（engine-local 实现范围）

| 上游语义 | engine-local 现状 | T0189 缺口 |
|---|---|---|
| 转 free 唯一路径 + 清簿记 | reclaim_bucket 同事务 | 无（基线） |
| journal boundary | -11 EAGAIN seam | 无（基线） |
| open bucket 保护 | 无 open 概念 | **新增 open_buckets 状态 + open/close API** |
| 设备可写 | 无 rw 状态 | **新增 rw_devs 状态 + set_device_rw API** |
| 重试分支 | worker 队列 + EAGAIN 轮转 | 无（T0190/T0191 基线） |
