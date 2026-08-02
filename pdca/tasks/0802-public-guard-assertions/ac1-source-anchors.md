# T0193 AC-1 源码锚点

修改前对照记录。本任务断言套件全部语义均以本地 bcachefs-tools 为唯一依据。

## 0. 聚合入口 ← bch2_check_allocations（recovery pass 语义）

- `fs/btree/check.c:1097-1160`：`bch2_check_allocations` 是 recovery pass
  单入口：guard state_lock/gc.lock → flush interior updates → 逐 phase 重算
  alloc/accounting 一致性（gc_start/alloc_start/mark_superblocks/gc_btrees/
  alloc_done/accounting_done），任何 phase 失败即 `bch_err_msg` 上报并带
  ret 返回。语义：一致性检查是 pass 级聚合，一次运行覆盖全部不变量，
  失败返回 errno，不修改状态。
- `fs/init/recovery.c:72/118/151`：check_allocations 在正常与降级 recovery
  路径均执行，并写入 `recovery_passes_required`——聚合检查是恢复的必要
  步骤。
- engine-local 映射：`verify_bucket_indexes`（engine.rs:622）已是该 pass 的
  engine-local 对应物；本任务新增 `verify_guard_invariants` 为守卫不变量
  的聚合入口，与其并列。

## 1. open 桶不得处于 free ← bch2_bucket_is_open_safe（discard 跳过语义）

- `fs/alloc/discard.c:344-347`：`bch2_bucket_is_open_safe(c, bucket.inode,
  bucket.offset)` 为真时跳过该桶（`s->open += bucket_size; return 0`）——
  open 桶绝不进入 discard/free 路径。
- `fs/alloc/discard.c:433-436`：同守卫在 discard 批量路径再次出现
  （`discard_bucket_fast` 入口检查）。两道检查均在持有 alloc key 之后
  执行，位置固定不可删减。
- `fs/alloc/discard.c:743`：`bch2_bucket_is_open_safe` 在 invalidates 路径
  同样跳过——open 桶与 free 状态互斥是全局不变量，非单路径偶然行为。
- engine-local 映射：`open_buckets: Mutex<BTreeSet<(u64,u64)>>`
  （engine.rs:435）与 discard_bucket 守卫（engine.rs:1010-1017）。
  断言：∀ (dev,off) ∈ open_buckets，alloc_v4(dev,off).data_type != FREE。

## 2. not_rw 设备桶不得转 free ← bch2_dev_get_ioref(WRITE)（skip 语义）

- `fs/alloc/discard.c:349-357`：`bch2_dev_get_ioref(c, dev, WRITE, ...)`
  失败（设备非 rw）时 `s->not_rw += bucket_size; return 0`——非 rw 设备
  桶不进 discard 路径。
- `fs/alloc/discard.c:654`：`discard_one_bucket_fast` 用
  `bch2_dev_get_ioref(c, ca->dev_idx, WRITE, ...)` 同守卫。
- `fs/alloc/discard.c:871`：`do_invalidates` 路径同守卫。
- engine-local 映射：`rw_devs: Mutex<BTreeSet<u64>>`（engine.rs:436）与
  discard_bucket 守卫（engine.rs:1018-1025）。断言：
  ∀ (dev,off) ∈ alloc FREE，dev ∈ rw_devs（否则该桶处于 not_rw 设备的
  free 状态）。

## 3. drop 无泄漏 ← bch2_open_buckets_stop（umount 关闭语义）

- `fs/init/fs.c:324`：`__bch2_fs_read_only` 在只读/销毁路径调用
  `bch2_open_buckets_stop(c, NULL, true)`——fs 关闭必须清理全部 open
  buckets。
- `fs/alloc/foreground.c:1171-1230`：`bch2_open_buckets_stop` 关闭全部
  write points 并释放 open bucket（`bch2_open_bucket_put`）。
- engine-local 映射：`impl Drop for EngineState`（engine.rs:1638-1673）
  open_buckets 非空即 panic（T0192 已实现，行为不改）。
  断言：提供 `open_bucket_count()` 查询，调用方可在 drop 前查询
  （等价于 fs 关闭路径的"无遗留"检查）。

## 4. run 后队列空 ← bch2_do_discards_fast_work（while-耗尽语义）

- `fs/alloc/discard.c:605-633`：fast_work while 循环持续 draining 直到
  队列耗尽；`bch2_fast_discard_bucket_add`（discard.c:643）darray 追加。
- engine-local 映射：`run_discard_worker`（engine.rs:1094-1138）返回 Ok
  当且仅当 inflight 队列耗尽；-11 轮转时队列非空是合法状态（T0191 语义）。
  断言：提供 `discard_queue_empty()` 查询，调用方在 worker Ok 后断言空；
  不改变 worker 行为（不自动校验，避免 -11 合法路径误报）。

## 对应 subvol 现状

- engine.rs:622-675：`verify_bucket_indexes`（已公开，聚合入口风格参照）。
- engine.rs:240-248：`DerivedStateMismatch` 枚举（断言失败变体扩展点）。
- engine.rs:435-436：`open_buckets` / `rw_devs` Mutex 集合（断言读取源）。
- engine.rs:434：`discard_inflight: Mutex<(VecDeque, BTreeSet)>`（队列查询源）。
- engine.rs:1010-1025：discard_bucket 现有 open/not_rw 守卫（断言语义来源，
  与断言互为实现与校验）。
- engine.rs:2948-3010：T0192 drop 泄漏定向测试（AC-5 切换点）。
- engine.rs:3040-3080：T0189/T0191 队列轮转定向测试（AC-5 切换点）。
