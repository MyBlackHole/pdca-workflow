# T0185 本地 bcachefs 源码对照审计

- `fs/init/recovery.c:68-118`: recovery 在主树恢复后按 explicit pass 检查 allocations、alloc
  info、btree backpointers 与 extents-to-backpointers；本任务将校验放在 rebuild 完成后、
  recovery 返回前。
- `fs/alloc/backpointers.c:900-1045`: bucket/backpointer mismatch 检查以 alloc bucket 为
  入口，并要求派生 backpointer 与主 extent 互相可定位。
- `fs/alloc/backpointers.c:1228-1404`: extents-to-backpointers 与 backpointers-to-extents
  两个方向分别扫描并报告 mismatch；Rust 校验器对应比较 primary-derived 集合及字段。
- `fs/alloc/check.c:141-235`: alloc key 校验要求 generation、dirty sectors 等字段与主记录
  一致；Rust 校验器至少比较 generation 与 dirty sectors，保留既有格式和字段布局。
- `fs/alloc/background.c:979-1045`: alloc 派生 key 的 generation/bucket 位置由现有 alloc
  key 维护路径确定；Rust 复用 members-v2 bucket geometry。

产品修改仅增加只读 raw primary scan、alloc/backpointer 集合比较，并在两条 recovery 入口
完成 rebuild 后调用校验；未接入 allocator、GC、LRU、stripe 或 VFS。
