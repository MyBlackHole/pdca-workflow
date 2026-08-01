# T0179 审计范围修正

用户指出 range key、空间分配、内部 btree 记录和 backpointer btree 未被纳入原审计。
该异议成立。

- `fs/btree/types.h:1260-1267` 把 `BKEY_TYPE_btree` 放入 transactional trigger
  集合。
- `fs/data/extents.h:419-446` 将 btree pointer 与 extent 的 key-op 绑定到
  `bch2_trigger_extent()`；`fs/alloc/buckets.c:894-924` 仅在 transactional/GC
  阶段更新引用、reconcile 等派生状态。
- `fs/alloc/buckets.c:681-684` 显示 extent pointer 的 transactional 分支在同一
  transaction 更新 alloc 并调用 `bch2_bucket_backpointer_mod()`。
- subvol 的 iterator 在 extents tree 上自动设置 `BTREE_ITER_is_extents`
  （`btree/iter.rs:83-87`），`bch2_trans_update_ip()` 会分派到
  `bch2_trans_update_extent()`（`btree/update.rs:1510-1513`）；内部节点使用
  `KEY_TYPE_btree_ptr_v2`（`btree/interior.rs:695-704`）。
- subvol 当前没有 `bch2_trigger_extent`、`bch2_trigger_alloc`、
  `bch2_bucket_backpointer_mod`、transactional runner 或 GC visited 模型；仅有
  backpointer key type 常量。

因此，原“无适用缺口”结论只能适用于公开 cookie/deleted 与 snapshot atomic
路径。对存储引擎 core 整体必须判为 partial，并以新的完整审计任务跟进。
