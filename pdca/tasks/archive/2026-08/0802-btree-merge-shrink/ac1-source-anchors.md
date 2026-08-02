# T0204 上游锚点记录（AC-1）：btree 前台合并（树收缩）

修改前逐段对照的本地 bcachefs-tools 源码（fs/btree/interior.c、
interior.h、commit.c）与 subvol 域内差异判定。

## 1. bcachefs merge 语义链（源码锚点）

| 组件 | 锚点 | 语义 |
|------|------|------|
| `btree_node_needs_merge(c, b, d)` | interior.h:194 | 门控：`min(sib_u64s[0], sib_u64s[1]) + d <= foreground_merge_threshold`；merging_disabled 静态分支（subvol 无此开关） |
| `bch2_foreground_maybe_merge` | interior.h:203 | wrapper：needs_merge 不满足直接返回 0；要求 path intent-locked |
| `__bch2_foreground_maybe_merge` | interior.c:2907 | 主体：边界门槛（min_key==POS_MIN → sib_u64s[prev]=U16_MAX；max_key==SPOS_MAX → sib_u64s[next]=U16_MAX）→ push srcs（prev/自身/next 左到右）→ srcs.nr==1 返回 → `compute_merge` 估算 → `btree_merge_topology_check` → update_start（锁升级）→ 重验 parent 一致性（锁后竞态窗口）→ 逐 src 拿写锁 → 分配 dsts → N→1 `bch2_btree_sort_into` 打包（seq=max(srcs)+1、min/max、format、topology_check、reset_sib_u64s）或 3→2 `btree_pack_into_dsts` → build_aux_trees → parent_keys（src→delete、dst→new key，同 .p 吞并）→ `bch2_btree_insert_node` 提交 → will_free_node + write_new_node + free_inmem + trans_node_add + `bch2_btree_update_done`（retire）；失败 `merge_fail_reset_sib_u64s` + 解锁 + update_free |
| `btree_merge_push_pos` | interior.c:2447 | 推兄弟进 srcs：边界跳过（sib_u64s=U16_MAX）、sib_u64s > threshold 跳过、path_get + traverse（nofill 优先，miss 用 evicted-size hash，再 miss 真读）、不同 parent 跳过（毒化） |
| `merge_node_u64s_and_format` | interior.c:2512 | 格式感知重算总 u64s（全部 b 在场用 `btree_node_u64s_with_format` 精确；否则 live_u64s 和） |
| `compute_merge` | interior.c:2832 | `nr_dsts = max(1, ceil(total / HIGHER_THRESHOLD))`（HIGHER=3/5 容量）；`nr_dsts >= srcs.nr` → 3-srcs 特例（丢大侧兄弟，`ceil(total / (max_u64s/2))` 重算）否则全毒化返回；nr_dsts==1 → 单 dst（format=new_f，max_key=末 src max）；nr_dsts==2 → `find_balanced_split` 分区（不可行且总字节 < 单节点 → 退回 1-dst，否则全毒化） |
| `merge_fail_reset_sib_u64s(_at)` | interior.c:2577/2591 | 失败毒化：`sib_u64s = live + sib_live`，超 HYSTERESIS（threshold+threshold>>2）则减去超出的 1/2，min(U16_MAX-1) |
| `btree_merge_topology_check` | interior.c:2399 | srcs 连续：`prev.max successor == next.min`，否则拓扑错误 |
| 常量 | btree/cache.h:191-195 | `THRESHOLD = max_u64s/3`、`HIGHER_THRESHOLD = max_u64s*3/5`、`HYSTERESIS = THRESHOLD + THRESHOLD>>2`；init.c:315 `c->btree.foreground_merge_threshold = THRESHOLD` |

## 2. 调用点（挂载对照）

| 调用点 | 锚点 | 语义 |
|--------|------|------|
| 常规 commit | commit.c:1446-1466 | 更新循环内：`u64s_delta` 累计（加新键 u64s、减 old_btree_u64s），`!same_leaf_as_next && !has_interior_updates` 边界处 `btree_node_needs_merge(c, b, u64s_delta)` → `trans_commit_merge`（BCH_WRITE_REF_trans 门控 + watermark hipri） |
| split 完成后 | interior.c:2308-2314 | `for (l = level+1; intent_locked(path, l) && !ret; l++) maybe_merge(path, l, flags)` 逐层向上 |
| node_merge_key 后 | interior.c:3369 | fsck/rewrite 路径（subvol 域内无此路径，范围外，不实现） |

## 3. subvol 域内差异判定

| # | bcachefs 设施 | subvol 对应 | 判定 |
|---|--------------|-------------|------|
| D1 | nofill + evicted-size hash（push_pos 分支） | 直接 `bch2_path_get` + `bch2_btree_path_traverse` | 域内简化：subvol 无 evicted-size hash 表；nofill 是性能优化，正确性不依赖 |
| D2 | `darray_merge_node` 动态数组 | 固定 `[MergeNode; 3]` + nr（srcs ≤ 3 恒成立：prev/自身/next） | 形式调整（约束 5），容量上界一致 |
| D3 | 3→2 `find_balanced_split`/`btree_pack_into_dsts` 分区 | 单 dst + 节点 grow（byte_order+1，split 既有机制 interior.rs:441-495） | 域内等效：subvol 节点容量可变，总键量超当前容量时 grow 单节点，收缩效果 ≥ 3→2；正确性由 format/容量自洽保证（split 同机制已验证） |
| D4 | watermark 门控（interior_updates/reclaim 分支） | 无 write buffer/reclaim watermark → 不省略门控判断，但条件恒不成立 | 语义对应：subvol 无 BCH_WATERMARK_interior_updates 路径，分支不可达（域内差异，非逻辑简化） |
| D5 | `u64s_delta`（新键 − old_btree_u64s） | commit 循环 `acc_u64s`（新增键和；delete 计 0） | 门控灵敏度差异：sib_u64s 本身是 cached estimate（bcachefs 也非精确），delta 近似只影响合并触发时机不影响正确性；merge 内部有 compute_merge 精确门控兜底 |
| D6 | `bch2_btree_update_start` 锁升级后重验 parent | push 时校验 parent 一致性（subvol 事务域无锁升级竞态窗口：commit 全程持 fs 锁 + 单写者） | 域内差异：重验是针对并发竞态（interior.c:3079 注释），subvol 无该竞态；push 时校验保留（对齐 interior.c:2487 同 parent 检查） |
| D7 | `bch2_btree_insert_node`（interior 更新提交）+ update_done retire 管线 | split 的 parent 替换模式（interior.rs:853-963：定位/删除旧 key + 插入新 key + set_dirty + retire_node）+ trans_node_add | 复用既有设施：subvol split 与 merge 共用同一 interior 更新路径 |
| D8 | `btree_node_rewrite_key` 调用点（interior.c:3369） | 无对应路径 | 范围外（域内无 fsck/rewrite 入口） |

## 4. subvol 复用设施清单

- `btree_buf_max_u64s`（interior.rs:9，节点容量 u64 数）→ THRESHOLD/HIGHER/HYSTERESIS 基数
- `bch2_btree_sort_into`（bset_build.rs:834，N→1 逐 src 打包）
- `bch2_btree_node_check_topology`（interior.rs:256）
- `btree_node_reset_sib_u64s`（interior.rs:338）
- `bch2_btree_node_lock_write`（interior.rs:351，写锁 + 自身 read 锁解除）
- split 的 parent 更新/分裂/root 创建路径（interior.rs:853-963/967-1059/753-851）
- `bch2_path_get`（iter.rs:1010）/ `bch2_btree_path_traverse`（iter.rs:1722）
- `bch2_bkey_format_init/add_key/add_pos/done`（bkey.rs:622/638/644/672）
- `bch2_btree_build_aux_trees`（bset_build.rs:748）
- `bch2_trans_node_add`（iter.rs:1138）、`bch2_btree_node_free_inmem`（split 内 retire_node 对应）

## 5. 测试设计锚点

- 删除压力：与 split_stress 对称的 delete_stress——批量 put 撑起多层树 → 批量 delete 收缩；断言：深度不增、节点数减少、逐节点 `bch2_btree_node_check_topology` + 全局键覆盖不变量（遍历所有叶节点收集键 == BTreeMap 模型）。
- 崩溃恢复：delete 压力 + sync 点 drop + open_persistent，replay 后拓扑有效 + 键集精确。
- 与既有逻辑键级模型（random_operations/split_stress）不冲突：物理节点布局对逻辑键级模型不可见，新增断言仅限物理层。
