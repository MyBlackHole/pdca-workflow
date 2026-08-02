# T0183 check-evidence：AC 对照表

## AC-1 源码对照锚点

- 读取：`alloc/buckets.c`（bch2_trigger_pointer 630-707、__mark_pointer
  612-628、bch2_bucket_ref_update 469-559）、`alloc/background.c`
  （bch2_trans_start_alloc_update 915-949）、`alloc/backpointers.h`
  （bch2_extent_ptr_to_bp 166-209）、`alloc/backpointers.c`
  （mod_nowritebuffer 162-183、backpointer_mod_err 118-160、
  check_extent_to_backpointers 777-825）。
- 产物：evidence/ac1-source-anchors.md（逐行锚点 + subvol 对应 + 差异判定）。

## AC-2 插入/覆盖/删除同事务派生维护

- 实现（T0182 提交 64e6a49）：trigger_pointer_derived（update.rs:2420）
  同事务更新 alloc（gen 校验 + dirty_sectors 增减）并写/删 bp（btree 8）；
  bch2_trigger_extent（2531）old/new 双分支；dev/bucket 合法性校验
  （trigger_pointer_validate 2283）。
- 测试：insert（3283 transactional_pointer_trigger...）、btree_ptr_v2
  insert+delete（3531 explicit_interior...）、**overwrite（本次新增
  extent_overwrite_moves_derived_state_to_new_pointer，subvol d259b46）**：
  alloc 3→5 扇区迁移、旧 bp 消失、新 bp 生成、check Ok。
- 无重复/悬挂/漏记：check_extents_to_backpointers 对 bp 集合去重检查
  （DuplicateBackpointer）+ 集合等价断言。

## AC-3 崩溃恢复与故障注入

- 恢复顺序：主键 norun replay → rebuild_derived_state（engine.rs:2079，
  保留运营字段 → 清派生树 → 主键投影重建 → 回填）→ 校验 gate → 发布。
- 故障注入：T0186 fault matrix（journal replay 后 / DuringDerivedRebuild /
  publication 前三 fault point 均报错）；主键+派生键同 journal entry
  原子性（3639 interior_pointer_commit_journals...）。
- norun replay 不产生派生键（3731）、clear+rebuild 恢复（3769）。

## AC-4 确定性验证器（两种来源）

- check_extents_to_backpointers（engine.rs:2380）：主 pointer 集合投影
  （expected_alloc + expected_bp）vs alloc/bp 树实际集合精确比对；
  gen 一致性、重复 bp、AllocSet/BackpointerSet mismatch。
- 来源覆盖：extent（3283）、btree_ptr_v2（3531/3639）两种均已测试。

## AC-5 全量验证

- lib 230 全过（串行 23.76s < 60s；并行 2 次全过）；btree_proptest 15
  全过（--test-threads=4，44.46s 基线）；fsck_cli 5 全过；fmt 通过。
- 备注：lib 并行偶发 1 failed 未复现（连续 3 次全过），与既有
  split_stress 并行 flaky 同类，验证基线 --test-threads=4。

## 范围边界

GC trigger、stripe-backpointer、完整 bucket LRU/free-index、双向
bp→extent 校验（T0185 结论限定方向 1）不在本任务。
