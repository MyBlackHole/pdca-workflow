# T0169 Do 证据 — commit 空间检查累加修复

来源：T0168 D1（CRITICAL）→ T0169 修复任务。
对应提交（subvol 仓库，按时间序）：

| 提交 | 内容 | 对应 PRD 修复方向 |
|------|------|-------------------|
| `30534a3`【B-T0169】engine | checkpoint → journal reclaim 迁移（含 btree 写路径相关回归基线） | 前置清理 |
| `702c2a6`【F-T0169】btree | split 前按同叶空间累积并扩容小节点 | 修复方向 1（AC-1/AC-2） |
| `6701bf8`【B-T0168】btree | 补 commit 插入剩余空间防御 + 同叶多 update 回归测试 | 修复方向 2/3（AC-3/AC-4） |

## AC-1：commit 空间检查对齐 commit.c 累加语义

`crates/subvol/src/btree/update.rs`（`bch2_trans_commit` 内，现约 1968-1988 行）：

```rust
if last_leaf.is_null() || last_leaf != b {
    acc_u64s = 0;
}
acc_u64s += required_u64s;
last_leaf = b;
if !bch2_btree_node_insert_fits(b, acc_u64s)
    && want_new_bset(c, b).is_null()
{
    bch2_btree_split_leaf(trans, path, u64s, 0); // 放不下 → split
    return btree_trans_restart(trans, ...);       // 重启事务
}
```

对照 `bcachefs-tools/fs/btree/commit.c:1083-1097`：`same_leaf_as_prev(trans, i)` 判同叶后 `u64s += i->k->k.u64s` 累加，再 `btree_key_can_insert`；放不下设 `*stopped_at = i` 并走 split/restart。subvol 按相邻 update 的同一 `b`（节点）累加 `acc_u64s`，语义一致。

## AC-2：放不下走 split/restart，无死循环无丢失

- split 复用既有 `bch2_btree_split_leaf` + `btree_trans_restart` 同步模型（T0169 PRD 第四条第 1 点指定复用路径）。
- 回归验证：`cargo test --lib` 173 全绿，覆盖并发写（4 写线程 × 24 键）、崩溃恢复（3 阶段进程级 crash）、持久化往返等路径，未出现死循环/数据丢失。

## AC-3：写入前剩余空间断言（等价 EBUG_ON）

`crates/subvol/src/btree/update.rs` `bch2_btree_bset_insert_key_inlined`（commit 写路径、`bch2_bset_insert` 调用前）：

```rust
assert!(
    (*insert).k.u64s as usize <= bch2_btree_keys_u64s_remaining(b),
    "bch2_trans_commit insert overflow: ..."
);
```

对照 `bcachefs-tools/fs/btree/commit.c:189-195`：`EBUG_ON(insert->k.u64s > bch2_btree_keys_u64s_remaining(b))` 位于 `bch2_btree_bset_insert_key_inlined`（commit.c:194）。断言放置位置与 bcachefs 原位一致；debug 构建触发即 panic。断言置于 commit 调用点而非 `bch2_bset_insert` 入口，避免误伤直接构造 fake 节点的既有单测（fake 节点不满足 remaining 计算，测试已验证）。

## AC-4：回归测试

`crates/subvol/src/engine.rs`：`single_transaction_many_keys_into_one_leaf_splits_without_overflowing`

- 单事务 32 键（position 1..=32，4-u64s value ≈ 9 u64s/键，累计 ≈ 288 u64s）写入 512B（64 u64s）初始节点，远超容量。
- 修复前：逐键 fits 检查全部通过 → `bch2_bset_insert` `copy_nonoverlapping` 越界写堆（PRD 现象，ASAN heap-buffer-overflow WRITE of size 40）。
- 修复后：acc_u64s 累计判空 → split/grow 成功；断言 commit 返回 Ok、scan 计数 32、verify 通过。

## 回归测试有效性验证

将该测试的 key 数改为 2 后运行（不触发容量边界）无法暴露缺陷；32 键序列覆盖"第 8+ 次插入时节点已满"的原崩溃窗口。另：即使累加逻辑被回退，AC-3 断言也会先于越界写触发 panic，双保险。

## 范围

仅改动 `update.rs`（防御）+ `engine.rs`（测试）；未引入 bcachefs 不存在的逻辑/结构（约束 12/13）。前窗口提交 `702c2a6` 同时含 interior.rs/update.rs 的 split 扩容（T0169 修复方向 1 的一部分：512B 小节点需扩容才能容纳 16×8-u64s）。
