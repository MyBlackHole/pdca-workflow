---
schema: pdca.asset/v1
id: ontology:domain/core-pointer-trigger-derived-chain
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-pointer-trigger-derived-chain/1.0.0
summary: pointer trigger 派生三件套与 AC-1 锚点模式（T0183）
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 pointer-trigger-derived-chain 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# pointer trigger 派生三件套与 AC-1 锚点模式（T0183）

## 适用场景

实现/审计 bcachefs pointer trigger 派生态（alloc + backpointer）时，
以本锚点为对照基准，避免凭记忆重写。

## upstream 三件套（buckets.c:630-707 bch2_trigger_pointer）

1. `bch2_extent_ptr_to_bp(c, btree_id, level, k, p, entry, &bp)`：构造 bp
   （键位 = POS(dev, offset<<extent_bp_shift + crc.offset)；值 = btree_id/
   level/data_type/bucket_gen=ptr.gen/bucket_len=btree_sectors 或 k.size/
   pos=k.p）。
2. `bch2_trans_start_alloc_update`（background.c:915）：定位/修改 alloc
   键（cached|intent；事务内存中已改的键直接复用，防读旧值——
   等价 subvol trigger_staged_key）。
3. `__mark_pointer`（buckets.c:612）：字段选择 has_ec→stripe_sectors /
   cached→cached_sectors / 否则 dirty_sectors；`bch2_bucket_ref_update`
   （469）：gen 校验链（ptr 新于桶 → insert 报错/delete 忽略；stale
   dirty 报错；stale cached 跳过）+ 混类型校验 + U32_MAX 溢出处理；
   insert 时 `alloc_data_type_set`。
4. `bch2_bucket_backpointer_mod`（backpointers.c:162）：insert 要求槽位
   deleted（否则 backpointer_mod_err → 恢复 pass）；delete 要求值匹配；
   delete 转 KEY_TYPE_deleted 后 trans_update。

## subvol 映射（btree/update.rs）

- trigger_pointer_validate（2283）≈ dev/bucket 合法性（insert→-1/delete→1）
- trigger_pointer_derived（2420）≈ 三件套（gen 校验、dirty_sectors
  checked_add/sub、写/删 bp btree 8）
- bch2_trigger_extent（2531）≈ old/new ptr 字节比较 + 先 old 后 new
  事务顺序
- engine.rs check_extents_to_backpointers（2380）= 方向 1 验证器：
  主 pointer 投影 vs alloc/bp 树精确集合比对

## 域内差异（记录在案，不违反约束 12/13）

1. **data_type 不入派生**：upstream insert 设 alloc.data_type=ptr
   data_type；subvol 的 data_type 由 alloc op 状态机管理（T0202 模型，
   FREE=0/BTREE=3/NEED_DISCARD=9），派生只维护 dirty_sectors+gen。
2. **delete 无 bp 匹配校验**：subvol 无写缓冲/恢复 pass 机制，delete
   直接删槽位，由验证器事后兜底。
3. bp data_type 内部编号（level==0→0/≠0→1）非上游 BCH_DATA 编号
   （约束 14 豁免）。

## 恢复顺序（T0181 合约）

主键 norun replay → 派生不可发布 → rebuild_derived_state（保留 alloc
运营字段 → 清 alloc/freespace/bp 派生树 → 主键投影重建 → 回填）→
校验 gate → 发布。fault：DuringDerivedRebuild。

## 测试模式

- insert：stage_extent_pointer 后断 alloc gen/dirty_sectors + bp 值
- overwrite：同 pos 二次插入（old/new 双非 deleted）→ alloc 减旧加新、
  bp 精确迁移（T0183 d259b46 新增）
- delete：old 触发减扇区 + bp 删除（dirty_sectors==0）
- norun：replay 不产生派生键
- 破坏性：删 alloc/bp 后验证器必须 Err
