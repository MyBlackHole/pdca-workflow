# T0194 AC-1 源码锚点

修改前对照记录。聚合入口语义以本地 bcachefs-tools recovery pass 驱动为
唯一依据。

## 0. 聚合入口 ← recovery pass 驱动（顺序执行 + 首个错误优先）

- `fs/init/recovery.c:68-98`：`__bch2_run_explicit_recovery_pass(c, msg,
  BCH_RECOVERY_PASS_check_topology, 0, &write_sb) ?: ret;` 逐 pass 执行，
  每个 pass 都运行（非短路），`?:` 保留首个错误（`ret = 新错误 ?: 旧错误`，
  等价 C 语义：若新调用返回非零则取其错误，否则保留旧值）。
- `fs/init/passes_format.h:55-98`：pass 定义表含依赖序标记
  （PASS_FSCK_ALLOC/PASS_ONLINE），check_allocations 依赖
  check_topology（BIT_ULL(BCH_RECOVERY_PASS_check_topology)）——
  顺序即依赖序：拓扑最基础，分配/守卫最上层。
- engine-local 映射：`verify_all()` 依次运行四个校验，每个都执行，
  返回首个 Err（`:?` 的 Rust 等价：逐次 `?` 语义改为记录首个错误继续），
  顺序 拓扑→派生状态→桶索引→守卫。

## 1-4. 四个被聚合校验（现状锚点，行为不改变）

| 校验 | engine-local | 上游对应 |
|------|--------------|----------|
| 拓扑 | verify（engine.rs:586-617） | bch2_btree_node_check_topology（btree/check.c） |
| 派生状态 | verify_derived_state（engine.rs:618-622） | check_extents_to_backpointers（T0185/T0186） |
| 桶索引 | verify_bucket_indexes（engine.rs:624-683） | check_allocations（btree/check.c:1097） |
| 守卫 | verify_guard_invariants（engine.rs:688-732，T0193） | bucket_is_open_safe / dev_get_ioref skip |

## 对应 subvol 现状

- engine.rs:586-732：四个校验 API（聚合对象）。
- engine.rs:29 处 verify_bucket_indexes + guard 测试断言（AC-3 切换点）。
- engine.rs:3500 属性测试逐 op 校验点（AC-5 切换点）。
