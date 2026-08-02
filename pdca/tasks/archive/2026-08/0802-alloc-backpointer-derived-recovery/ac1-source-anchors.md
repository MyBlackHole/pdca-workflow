# T0183 AC-1：bcachefs 源码等价语义锚点（alloc/backpointer 派生）

对照基准：`/home/black/Documents/bcachefs-tools/fs/alloc/`（2026-08-02 现场读取）。

## 1. bch2_trigger_pointer（buckets.c:630-707）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| 638 | `insert = !(flags & BTREE_TRIGGER_overwrite)` | update.rs trigger_extent_pointers(insert) |
| 641 | `bch2_extent_ptr_to_bp(c, btree_id, level, k, p, entry, &bp)`：构造 bp，`*sectors = insert ? bucket_len : -bucket_len` | update.rs:2420-2441（bp 构造 + 扇区符号） |
| 645-655 | dev==BCH_SB_MEMBER_INVALID：仅 stripe/EC 走 stripe_backpointers，否则跳过（无 EC 时返回 0） | subvol 无 EC：validate 拒绝无效 dev |
| 657-670 | `bch2_dev_tryget_noerror`：设备缺失 → insert 报错 / delete 忽略 | trigger_pointer_validate:2290-2292（insert→-1 / delete→1=跳过） |
| 672-679 | `PTR_BUCKET_POS` + `bucket_valid`：桶越界 → insert 报错 / delete 忽略 | trigger_pointer_validate:2306-2311 |
| 681-685 | 事务路径：`bch2_trans_start_alloc_update`（读/改 alloc v4 键）→ `__mark_pointer` → `bch2_bucket_backpointer_mod` | trigger_pointer_derived:2432-2496（读 alloc → 改 → 写 bp） |
| 687-704 | BTREE_TRIGGER_gc 分支（内存桶状态） | 不在范围（无 GC） |

## 2. __mark_pointer（buckets.c:612-628）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| 619-621 | 字段选择：`has_ec → stripe_sectors`、`cached → cached_sectors`、否则 `dirty_sectors` | trigger_pointer_derived:2450-2459（仅 dirty_sectors；subvol 无 EC，cached ptr 无写入路径） |
| 622-623 | `bch2_bucket_ref_update(...)`：gen 校验链 + 扇区增减 | 见下 |
| 625-626 | **insert 时 `alloc_data_type_set(a, ptr_data_type)`** | subvol 派生不设 data_type（data_type 由 alloc op 状态机管理，T0202 域）——记录差异 |

## 3. bch2_bucket_ref_update（buckets.c:469-559）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| 479 | `inserting = sectors > 0` | — |
| 483-493 | `gen_after(ptr->gen, b_gen)`：ptr gen 比桶新 → insert 报错 / delete 忽略 | trigger_pointer_derived:2436-2438（insert 且 alloc.gen≠0 且不等 → -1；delete 无校验=上游忽略） |
| 495-505 | gen 过旧（>BUCKET_GC_GEN_MAX）→ 报错 | 范围外（无 GC） |
| 507-518 | stale cached（b_gen≠ptr.gen 且 cached）→ 返回 1 跳过 | subvol 无 cached 写入路径 |
| 520-531 | stale dirty（b_gen≠ptr.gen）→ 报错 | 覆盖于 2436-2438（insert 校验） |
| 533-542 | `bucket_data_type_mismatch`：桶内混类型 → 报错 | subvol 派生不设 data_type（同 2 的记录差异） |
| 544-555 | 扇区溢出（>U32_MAX）→ 归零并报错（insert throw / delete 忽略） | trigger_pointer_derived:2450-2459 checked_add/sub → -1 |
| 557 | `*bucket_sectors += sectors` | 2453/2457 |

## 4. bch2_extent_ptr_to_bp（backpointers.h:166-209）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| 170-171 | bp 键位 = POS(dev, ptr.offset << extent_bp_shift + crc.offset)；subvol extent_bp_shift=0 → POS(dev, offset) | update.rs:2476 |
| 196-203 | bp 值：btree_id/level/data_type/bucket_gen=ptr.gen/bucket_len=ptr_disk_sectors(level?btree_sectors:k.size)/pos=k.p | update.rs:2480-2488（bucket_len 用 BCH_SB_BTREE_NODE_SIZE 或 k.size） |
| 205-209 | 旋转盘 RECONCILE_PHYS、EC ERASURE_CODED 位 | 范围外（无 EC/旋转盘判定） |
| — | **data_type = bch2_bkey_ptr_data_type(k,p,entry)**（键类型决定：extent→user/btree_ptr→btree） | subvol 用 level==0→0/level≠0→1（内部编号域，非上游 BCH_DATA 编号；约束 14 豁免） |

## 5. bch2_bucket_backpointer_mod（backpointers.h:108-125 / .c:162-183）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| .c:167-175 | peek_slot 校验：insert 要求槽位 deleted；delete 要求存在且值匹配（否则 backpointer_mod_err → 恢复 pass 或报错） | update.rs:2477-2478 delete 直接 trigger_delete_value(8, bp_pos) 无匹配校验——记录差异（subvol 无写缓冲/恢复 pass 机制，delete 路径由验证器事后兜底） |
| .c:177-180 | delete 时转 KEY_TYPE_deleted | trigger_delete_value（KEY_TYPE_deleted 隐式） |
| .c:182 | `bch2_trans_update` | 同 |

## 6. 验证器（backpointers.c）

| 函数 | 语义 | subvol 对应 |
|------|------|------------|
| check_extent_to_backpointers（777-825） | 逐 ptr：构造 bp → 检查 bp 存在（check_bp_exists）或重插 | engine.rs:2380 check_extents_to_backpointers（方向 1：主指针投影 vs 派生集合精确比对） |
| check_backpointers_to_extents（1384+） | bp → 主键反向校验 | 范围外（T0185 结论：验证器不实现双向，方向 1 足够） |

## 7. bch2_trans_start_alloc_update（background.c:915-949）

| 行 | 语义 | subvol 对应 |
|---|------|------------|
| 919-921 | BTREE_ITER_cached|intent 定位 alloc 键 | trigger_read_alloc:2346-2357 |
| 942-944 | 已在事务内存中的 alloc 键直接复用（防重复读旧值） | trigger_staged_key:2320-2327（检查 staged update） |

## 8. 恢复顺序（T0181 合约 + recovery.c）

主键 norun replay → 派生状态不可发布 → rebuild_derived_state（engine.rs:2079：
保留 alloc 运营字段 → 清 alloc/freespace/bp 派生树 → 主键投影重建 → 回填）
→ 校验 gate（check_extents_to_backpointers）→ 发布。fault 点：
DuringDerivedRebuild（T0186）。

## 结论

派生链路（trigger/rebuild/validator/fault）由 T0181/T0182/T0185/T0186/T0187
实现并提交（subvol 64e6a49/e857bf1/336c570/d6f11a1 及 T0187 系列）。T0183
增量 = 覆盖（overwrite）场景专项测试（AC-2 明确要求插入/覆盖/删除三态）+ 全量验证。
记录差异（data_type 不入派生、delete 无 bp 匹配校验）经核对为 subvol 域内设计，
与 T0202 组合模型（data_type 由 alloc op 状态机管理）一致，不违反约束 12/13。
