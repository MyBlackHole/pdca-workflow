# PRD — T0169 修复 commit 空间检查未累加同 leaf 多 update 导致的堆越界写

来源：T0168（0801-btree-core-completeness）审查缺陷 D1（CRITICAL），检查阶段已确认。

## 一、现象

- 测试 `engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 单独运行时 SIGABRT：`free(): invalid next size`。
- ASAN 复现：heap-buffer-overflow，WRITE of size 40。
- 崩溃点：`crates/subvol/src/btree/bset_update.rs:188` `bch2_bset_insert` 的 `copy_nonoverlapping`（key 段越界写，`where_` 超出节点容量）。

## 二、复现

```bash
cargo test --lib engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root
RUSTFLAGS="-Zsanitizer=address" cargo +nightly test --lib engine::tests::checkpoint_pages_are_cow
```

## 三、根因（T0168 已确认，三要点源码抽查通过）

1. **主因**：`bch2_trans_commit` 空间检查（`crates/subvol/src/btree/update.rs:1953-1975`）对每个 update 独立调用 `bch2_btree_node_insert_fits(b, required_u64s)` 判空，**未累加同一 leaf 多个 update 的累计占用**。16 个 8-u64s key 各自通过空节点检查，但 512B 节点（=64 u64s）在第 8 次插入时已满仍继续写入 → 越界。
2. **bcachefs 对照**（`/home/black/Documents/bcachefs-tools/fs/btree/commit.c:1083-1097`）：`same_leaf_as_prev(trans, i)` 判断后 `u64s += i->k->k.u64s` 累加，再 `btree_key_can_insert(trans, b, u64s)`；放不下即 `*stopped_at = i` 中止 commit 并触发 split/restart。subvol 缺失此累加语义。
3. **次要防御缺失**：bcachefs `bch2_btree_bset_insert_key_inlined`（commit.c:194）有 `EBUG_ON(insert->k.u64s > bch2_btree_keys_u64s_remaining(b))`；subvol `bch2_bset_insert` 仅有局部 `new_u64s >= 0` 断言，无节点容量剩余检查。

## 四、修复方向（必须对齐 bcachefs 语义，禁自有逻辑）

1. 在 `bch2_trans_commit` 的空间检查循环中对**同一 leaf** 的 update 累加 `u64s`（对照 commit.c 的 `same_leaf_as_prev` 语义：相邻且 path/level 相同视为同 leaf），以累计值调用 `bch2_btree_node_insert_fits`；放不下时走现有 split_leaf + `trans.restarted = 4` 重启路径（subvol update.rs:1983-1990 已有同步模型实现，复用其返回语义）。
2. 在 `bch2_bset_insert` 写入前补节点剩余空间断言（等价 EBUG_ON：`key_u64s + val_u64s <= bch2_btree_keys_u64s_remaining(b)`），debug 构建触发即 panic，防回归。
3. 回归测试：单事务向同一 leaf 写入超节点容量的 key 序列（≥16 个 8-u64s，如 checkpoint COW 场景），断言不崩溃、全部 key 落盘、提交后节点分裂语义正确。

## 五、验证标准

- `cargo test --lib` 全绿（含原崩溃测试 `checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root`）。
- ASAN 运行 `engine::tests::checkpoint_pages_are_cow` 无报告。
- 新增回归测试覆盖多 update 同 leaf 累计场景（含节点容量边界）。
- 单测总时长 < 1 分钟（项目约束 9）。

## 验收标准

- [ ] AC-1: commit 空间检查对齐 commit.c 累加语义（同 leaf 累加 u64s 后判空）——验证方式：源码对照 + 代码审查
- [ ] AC-2: 放不下时正确走 split/restart 路径，无死循环、无数据丢失——验证方式：测试 + 审查
- [ ] AC-3: `bch2_bset_insert` 写入前有剩余空间断言（等价 EBUG_ON）——验证方式：源码审查
- [ ] AC-4: 新增回归测试（多 update 同 leaf 超容量序列）——验证方式：测试存在且通过
- [ ] AC-5: 原崩溃测试恢复通过，`cargo test --lib` 全绿，ASAN 无报告——验证方式：命令验证

## 七、范围与约束

- 修复范围仅限 `crates/subvol/src/btree/update.rs`（commit 空间检查）与 `bset_update.rs`（断言），不扩展其他缺陷（D2-D6 不在本任务）。
- 必须遵守项目 AGENTS.md 14 条编码约束：以 `/home/black/Documents/bcachefs-tools` 为唯一对照基准，行为逻辑对齐 commit.c，禁止自有逻辑分支；提交使用 bug-commit-format（缺陷描述/根因/方案/影响/性能）。
