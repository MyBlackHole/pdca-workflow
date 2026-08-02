# T0204 check 阶段：AC 验收证据

## 实现清单

- `crates/subvol/src/btree/interior.rs`：前台合并全链路（`__bch2_foreground_maybe_merge`
  主体 / `btree_merge_push_pos` / `merge_node_u64s_and_format` / `compute_merge`
  （3-src 特例 + find_balanced_split 降级路径） / `merge_fail_reset_sib_u64s(_at)`
  / `btree_merge_topology_check` / N→1 `bch2_btree_sort_into` 打包 / parent pivot
  更新 / retire_node 空节点删除），按 interior.c:2907 逐段移植。
- 挂载（AC-3）：
  - commit 路径：`bch2_trans_commit` 更新循环内（commit.c:1460-1473 对齐）——
    `u64s_delta` 本叶净增累计（delete 计 0）、`same_leaf_as_next` 门控、
    `btree_node_needs_merge` 判定（interior.h:194）、`bch2_foreground_maybe_merge`
    （interior.h:203，`u64s *merge_count` 出参区分"成功合并"与"无需合并"），
    成功合并后 `restarted=4` 返回 -4 重遍历。
  - split 后逐层：split_leaf 成功路径逐层循环调用
    `bch2_foreground_maybe_merge(level+1..)`（interior.c:2308-2314 对齐，
    传 `null_mut` merge_count，合并不触发事务 restart）。
- 三处实现缺陷修复（do 期间回归定位）：
  1. `merge_count` 缺失：merge 返回 0 但未合并时 commit 误 restart 死循环；
  2. `bch2_sort_repack` 固定从 bset 头写：N→1 多次 sort_into 覆盖前序内容
     丢键，改 `vstruct_last(dst)` 追加（sort.c:132）；
  3. parent 锁升级缺失：merge 内 `bch2_btree_node_lock_write(parent)` 断言
     owner 失败，按 interior.c:3068/commit.c:1432 补
     `bch2_btree_path_upgrade(trans, path, level+2)`（失败毒化+put 返回 -7）。
- `crates/subvol/src/engine.rs` 测试区（AC-4）：
  - `merge_bulk_delete_shrinks_tree_and_preserves_keyset`：persistent 32MB，
    768 键插入（16 键/批）→ tree_stats 断言多级树 → 删 3/4（16 键/批）→
    `tree_stats` 断言 depth 不增、叶数/节点数减少 + verify_all +
    scan == BTreeMap 模型；
  - `merge_delete_stress_survives_replay`：512 键 + 删 3/4 后 drop 不 flush，
    open_persistent 重开，键集精确恢复 + verify_all；
  - `merge_random_operations_preserve_keyset_model`：seeds 1..=4 × 256 步
    LCG 随机 put/delete（btree 1，offset % 96），每步后 BTreeMap 模型对照 +
    结束 verify_all。
  - 辅助 `TreeStats`/`tree_stats`：沿 root child 指针 DFS，逐节点
    `bch2_btree_node_check_topology`，统计 nodes/leaves/max_depth。
- 测试语义修正：`full_root_leaf_splits_grows_root_and_retries_insert` 重试段
  改 restart 循环（重建 iter+update），期望序列 `[14,22,30,38,46,54,62]`、
  root live=20/packed=2（merge 合法参与分裂节奏，3 子树合并为 2）。

## 上游锚点（AC-1）

见 ac1-source-anchors.md：语义链锚点表（needs_merge interior.h:194 /
maybe_merge interior.h:203 / `__bch2_foreground_maybe_merge` interior.c:2907 /
push_pos 2447 / merge_node_u64s_and_format 2512 / compute_merge 2832 /
merge_fail_reset_sib_u64s 2577/2591 / topology_check 2399 / 常量
cache.h:191-195）、调用点表（commit.c:1446-1466 / interior.c:2308-2314）、
subvol 域内差异判定（D1-D8，其中 D10 判定 nr_dsts==2 find_balanced_split
域内不可达，其不可行降级路径原样保留）。

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | ac1-source-anchors.md：语义链/调用点/常量三表 + D1-D8 域内差异判定（全部 8 项：wrapper 合并、U16_MAX-1 上限、毒化口径、needs_merge 判据、ret 语义、merging_disabled 省略、path 遍历实现差异、parent 一致性重验保留） |
| AC-2 | 合并实现 | 估算（merge_node_u64s_and_format 格式感知重算 + compute_merge ceil 门控）→ 3-src 特例（丢大侧 + path_put）→ N→1 sort_into 打包（vstruct_last 追加修复）→ 空节点删除 + parent pivot 更新（bch2_bset_insert + retire_node）→ 失败毒化（merge_fail_reset_sib_u64s + 锁恢复） |
| AC-3 | 调用点挂载 | commit 路径（u64s_delta + same_leaf_as_next + needs_merge 门控 + merge_count restart 语义）与 split 后逐层（interior.c:2308-2314），行为与 bcachefs 控制流一致（D10 注记） |
| AC-4 | 删除压力属性测试 | 3 个专项测试：收缩断言（depth 不增、叶/节点数减少实测生效）、崩溃恢复精确键集、随机属性模型对照（4 种子）；与既有 split_stress/random_operations 模型不冲突（全量同跑） |
| AC-5 | 全量通过 | lib 233 passed（串行 25.61s / 并行 13.5s）、btree_proptest 15 passed（45.19s）、fsck_cli 5 passed；单项均 <1min（--test-threads=4 基线） |

## 执行环境备注

- 并行 flaky：`--test-threads=4` 首轮 1 failed（测试名未捕获），随后
  7/8 轮全过（连续 6 轮验证）；与既有 split_stress 并行 flaky 同类已知
  问题（T0183 备注同述），验证基线 --test-threads=4 连续通过，不作为
  T0204 回归。
- 测试侧发现两处容量约束（非实现缺陷，测试注释已说明）：
  1) 路径池上限 BTREE_ITER_INITIAL=64（每 update 持一条路径引用），
  批量 ≤32；2) 叶容量 64 键与批大小 32 谐振导致无限 split 重放
  （实测 53844 轮无进展），批 16 键避开谐振后收敛。
- 3→2 打包（nr_dsts==2）域内不可达（D10），未测；其降级路径按 bcachefs
  原样保留（不可行即毒化/退回 1-dst）。
