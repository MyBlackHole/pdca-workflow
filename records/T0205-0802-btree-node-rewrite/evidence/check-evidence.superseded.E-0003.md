# T0205 check 阶段：AC 验收证据

## 实现清单

- `crates/subvol/src/btree/interior.rs`：`bch2_btree_node_rewrite` 主体
  （interior.c:3276-3343 逐段移植）——path 校验（-5）→
  `bch2_btree_path_upgrade` 锁升级（interior.c:3068，同 merge 挂载点，失败 -7）
  → `bch2_btree_node_lock_write(b)`（失败 -10）→
  `bch2_btree_node_alloc_replacement`（interior.c:593-616：calc_format →
  format_fits 回退旧格式（严格小于，interior.c:346-361）→ seq+1 → min/max
  继承 → `bch2_btree_sort_into` 全键搬移 → 容量断言 + topology 校验 +
  `btree_node_reset_sib_u64s` + `bch2_btree_build_aux_trees`）→
  `bch2_path_get_unlocked_mut` + `btree_path_take_new_node`（路径换新）→
  parent 分支（`bch2_bset_insert` 同位置替换 pivot，journal replay 覆盖检查）
  / root 分支（root.key = child_ptr 自指针 + transition CLEAN + set_dirty +
  `bch2_btree_set_root_for_read`）→ retire_node 旧节点释放 → 失败路径
  release_node + 解锁 + path_put（-7/-8/-10/-12 四态恢复）。
- 挂载（AC-3）：`crates/subvol/src/engine.rs` 公共 API：
  `rewrite_node`（rewrite_pos 语义，assert level != 0 对齐 BUG_ON(!level)）、
  `rewrite_node_key`（rewrite_key 语义，btree_ptr_v2 hash 匹配否则
  Transaction(-2)=ENOENT）；二者经 `lock_fs()` 单写者域调用
  `rewrite_node_locked`/`rewrite_node_key_locked`（iter init depth=level-1
  对齐 interior.c:3373 的 level-1/min_level 遍历约定）。
- 测试区（AC-4）7 个专项：
  - T1 `rewrite_leaf_node_pos_preserves_keyset_and_bumps_seq`：叶重写 →
    seq+1、parent pivot 指向新节点（mem_ptr 校验）、min/max 继承、scan 一致、
    verify_all；
  - T2 `rewrite_internal_node_keeps_subtree_visible`：内部节点（root level
    >=2）重写 → depth 不变、子树全键可遍历、keyset 一致；
  - T3 `rewrite_root_self_pointing_key_and_deep_scan`：root 重写 → root.key
    自指针、level 不变、深遍历一致；
  - T4 `rewrite_key_hash_mismatch_returns_enoent`：stale seq → -ENOENT 且
    节点不动；live key → 重写 seq+1；
  - T5 `rewrite_invalid_path_and_double_rewrite_no_orphan_paths`：path 0 未
    分配 → -5、树不动；连续两次重写 → seq 单调 +2、无悬挂路径；
  - T6 `rewrite_survives_crash_and_flush_reopen`：sync 后 rewrite → drop 不
    flush 重开 → 精确键集 + verify_all；flush + reopen 同样保持；
  - T7 `rewrite_random_operations_preserve_keyset_model`：4 种子 × 256 步
    随机 put/delete + 随机叶/内部重写 → BTreeMap 模型一致 + verify_all。
- 存量 flake 修复（非 T0205 引入，随提交附带）：`drop_detects_unclosed_`
  `open_bucket_leak` 在 drop 前显式停止并 join reclaim worker，消除
  Weak::upgrade 窗口期 Arc 计数 2→1 导致的断言跳过（baseline 对照同样
  失败 1/12，属存量问题）。

## 上游锚点（AC-1）

见 ac1-source-anchors.md：语义链锚点表（rewrite 主体 interior.c:3276-3343 /
alloc_replacement 593-616 / format_fits 346-361 / rewrite_key 3345-3359 /
rewrite_pos 3373-3388 / async_btree_rewrite 3400-3459 / 调用点 read.c:1243）、
调用点挂载对照（显式重写挂载、fsck/scrub 与 GC 触发为范围外）、域内差异
判定 D1-D10（update 对象 → pending_interior、async 队列 → 同步 API、
set_root → set_root_for_read + child_ptr 自指针、format_fits 移植组合等）。

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | ac1-source-anchors.md：语义链/调用点/差异判定三表 + 测试设计锚点 T1-T7（53 行） |
| AC-2 | 重写实现 | alloc_replacement 全链（calc_format 复用 interior.rs:1411 + format_fits 回退严格小于 + seq+1 + sort_into + reset_sib_u64s + build_aux_trees）→ 路径换新（take_new_node）→ parent/root 分支替换 → retire 旧节点 |
| AC-3 | 公开入口挂载 | rewrite_node/rewrite_node_key（assert level != 0 / hash 匹配 -ENOENT），单写者域经 lock_fs 调用；行为与 bcachefs 控制流一致（D8：rewrite 不触发事务 restart） |
| AC-4 | 测试覆盖 | 7 个专项测试：叶/内部/root/rewrite_key hash 匹配/失败注入/崩溃恢复/属性模型（T1-T7 与 PRD 锚点表一致） |
| AC-5 | 全量通过 | lib 240 passed（10.6s）、btree_proptest 15 passed（42.7s）、fsck_cli 5 passed（0.04s）；单项均 <1min；修复后 10/10 全量稳定性验证 |

## 代码审查结论（code-review-checklist 双轴）

标准轴：
- 失败路径完整性：-7（path_upgrade）/-8（parent 未找到旧键）/-10（lock
  write）/-12（alloc 失败）四态均先释放 n（release_node：clear_dirty +
  FREEABLE 转移或 data/mem free）+ 解锁 b（必要时 parent）+ path_put
  new_path，无悬挂引用；与 interior.c err_free_update 路径语义对应。
- 内存安全：所有指针访问先判 null（b/data/n）；`node_value_words`、
  `encode_key` 的 u64s 上限检查（BKEY_VAL_U64S_MAX）防越界；rewrite 内
  alloc_zeroed 以 `1usize << byte_order` 精确容量 + 断言非空。
- 锁序：b（写）→ parent（写）→ 释放 b → 释放 parent → 释放 n，与
  merge/split 已验证模式一致；失败路径释放顺序与获取顺序逆序。
- 持久化：parent 分支 set_dirty(parent)、root 分支 transition CLEAN +
  set_dirty(n) 保证 journal-first 落盘；T6 崩溃恢复实测通过。
- 未发现 Blocking 或 Warning 级问题。

规范轴：
- 未新增 bcachefs 不存在的函数（约束 8）：全部行为逻辑均在 interior.c
  对应锚点中找到依据。
- 未引入自有结构体（约束 13）：复用既有 btree/btree_update/btree_path。
- 差异点均已在 D1-D10 判定中记录（约束 12），无未申报的逻辑分支。
- 范围无蔓延：未动 fs 层 type/btree id 语义（约束 14 豁免），未引入新依赖。

结论：标准轴 0 个 Blocking / 0 个 Warning；规范轴 0 个 Blocking。
