# T0187 桶分配回收与反向引用链路结论

## 结论

**通过（最小范围）**。alloc bucket candidate、占用、need_discard/free 回收、generation
复用、freespace 派生索引、backpointer 保护与 recovery rebuild 已实现并通过验证。

## 验证

- 本地 bcachefs 对照审计已登记：`buckets.c`、`background.c`、`backpointers.c`、`discard.c`、`recovery.c`。
- `cargo test --workspace --all-targets` 通过；subvol 单元测试 187/187 通过。
- `cargo fmt --all -- --check` 与 `git diff --check` 通过。
- 覆盖 generation stale 拒绝、geometry 边界、freespace generation 编码、事务 restart/ENOMEM 重试及恢复派生重建。

## 范围边界

完整 discard worker、open-bucket GC、后台 GC/LRU、stripe/EC 与 VFS 不属于本任务范围，后续如需实现应创建独立任务。
