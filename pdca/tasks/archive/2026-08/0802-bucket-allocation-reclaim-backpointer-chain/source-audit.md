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

Rust 对应实现锚点：`crates/subvol/src/engine.rs:614-815` 提供 freespace 索引校验、
candidate 优先选择、free→btree 占用和 need_discard→free 回收；`crates/subvol/src/engine.rs:1467-1635`
在 recovery rebuild 中清理并重建 alloc/backpointer/freespace 派生树，保留 alloc 的
`data_type/gen/oldest_gen` 主状态；`crates/subvol/src/btree/update.rs` 的 bucket 状态测试覆盖
单事务状态序列与 stale-generation 拒绝。实现仍是 PRD 明确的最小 allocator/reclaim 核心，
不包含完整 discard worker/open-bucket GC。
