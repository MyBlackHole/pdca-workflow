# T0187 本地 bcachefs 源码对照审计

- `fs/alloc/buckets.c:469-553`：`bch2_bucket_ref_update()` 处理 pointer generation、stale
  pointer、bucket data type mismatch 和 sector overflow。
- `fs/alloc/buckets.c:584-704`：`bch2_trigger_pointer()` 先映射 bucket，再在 transactional
  分支更新 alloc 与 backpointer；insert/delete 错误分支不同。
- `fs/alloc/background.c:1242-1410`：`bch2_trigger_alloc()` 处理 nonempty→need_discard、
  free、generation bump、freespace index、bucket_gens 和 device counters。
- `fs/alloc/check.c:141-235`：`bch2_check_alloc_key()` 校验 device:bucket、need_discard、
  freespace 与 bucket_gens 交叉一致性。
- `fs/alloc/backpointers.c:900-1404`：extent↔backpointer 双向 mismatch 扫描；回收前必须能
  定位所有反向引用。
- `fs/alloc/discard.c`：need_discard 到 free 的回收前置条件与 open bucket 保护。
- `fs/init/recovery.c:68-118`：recovery explicit allocation/backpointer passes。

当前 Rust 已有 pointer-derived alloc/backpointer、generation 校验与 recovery validator；
T0187 尚未开始实现 bucket candidate、state transition、freespace/generation index 或 reclaim。
