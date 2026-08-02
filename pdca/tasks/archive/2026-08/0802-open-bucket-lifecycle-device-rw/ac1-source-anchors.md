# T0192 AC-1 源码锚点

修改前对照记录。本任务三个改动点均以本地 bcachefs-tools 为唯一依据。

## 1. drop 泄漏检测 ← bch2_open_buckets_stop（umount 关闭语义）

- `fs/init/fs.c:324`：`__bch2_fs_read_only` 在 fs 只读/销毁路径调用
  `bch2_open_buckets_stop(c, NULL, true)`——文件系统关闭时必须清理全部
  open buckets，不允许遗留。
- `fs/alloc/foreground.c:1171-1230`：`bch2_open_buckets_stop` 关闭全部
  write points（对 device=NULL 时遍历 `write_points[]`、copygc/reconcile/
  btree write point），并释放 reserve_cache 与 partial 列表中的 open
  buckets（`bch2_open_bucket_put`）。语义：open bucket 有明确的生命周期
  终点（fs 关闭），不存在"永开"状态。
- engine-local 映射：`StorageEngine::drop` 等价 umount/只读关闭；此时
  `open_buckets` 非空即调用方未配对 close，panic（BUG_ON 风格）暴露泄漏。

## 2. rw_devs 按 sb 初始化 ← bch2_dev_allocator_add/set_rw

- `fs/alloc/background.c:1723-1728`：`bch2_dev_allocator_add`（设备上线）
  调用 `bch2_dev_allocator_set_rw(c, ca, true)`——设备加入即置 rw，
  不依赖硬编码设备号。
- `fs/alloc/background.c:1663-1689`：`bch2_dev_allocator_set_rw` 按
  `ca->mi.data_allowed` / `durability` 逐 data_type 更新
  `rw_devs[data_type]` 位图，`rw_devs_change_count++`。
- `fs/sb/members.h:134-135`：`for_each_rw_member_rcu` 遍历
  `allocator.rw_devs[BCH_DATA_free]`（all rw devs）——rw 设备集合与
  online 成员集合一一对应（set_rw 上线即 true，remove 下线即 false）。
- engine-local 映射：当前 `rw_devs: BTreeSet::from([0])`（engine.rs:494）
  为硬编码；改为创建/attach 后按 `devs_online`（members.h devs_online
  predicate，subvol engine.rs:2293-2294 在 configure_persistent_journal
  设置 dev 0）推导初始集合，对应"上线即 rw"。

## 3. set_device_rw(false) 拒绝 ← bch2_dev_allocator_remove

- `fs/alloc/background.c:1690-1722`：`bch2_dev_allocator_remove`（设备下线）
  顺序：①`bch2_dev_allocator_set_rw(c, ca, false)` 先移除可写标记；
  ②`bch2_recalc_capacity`；③`bch2_open_buckets_stop(c, ca, false)` 关闭
  该设备 open buckets；④`closure_wait_event(&open_buckets_wait,
  !bch2_dev_has_open_write_point(c, ca))` 等待该设备 open write point
  清空后才完成下线。
- `fs/alloc/background.c:1650-1662`：`bch2_dev_has_open_write_point` 遍历
  open_buckets 检查该设备是否存在 valid open bucket（`ob->dev == ca->dev_idx`）。
- engine-local 映射：无并发 I/O 与阻塞等待，`set_device_rw(dev, false)`
  时若 `open_buckets` 含该设备桶，返回 -16 拒绝下线（等待语义的非阻塞
  等价，与 reclaim/discard 守卫同码）；设备清空后允许下线。

## 对应 subvol 现状

- engine.rs:494：`rw_devs: Mutex::new(BTreeSet::from([0]))`（待改，AC-3）。
- engine.rs:779-815：`open_bucket`/`close_open_bucket`/`set_device_rw`
  （T0189 新增，AC-4 在此基础上加拒绝守卫）。
- engine.rs:1602-1625：`impl Drop for EngineState`（AC-2 注入点）。
- engine.rs:2293-2294：`fs.devs_online.d[0] |= 1`（AC-3 推导依据）。
- btree/bset.rs:20-32：`bch_devs_mask { d: [usize; 4] }` +
  `bch2_dev_idx_is_online`（AC-3 遍历工具，与上游 members.h
  devs_online 位图一致）。
