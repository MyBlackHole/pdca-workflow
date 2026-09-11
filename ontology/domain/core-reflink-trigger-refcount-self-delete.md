---
schema: pdca.asset/v2
id: ontology:domain/core-reflink-trigger-refcount-self-delete
type: domain
layer: Knowledge
status: active
summary: reflink 触发器计分 + 归零自删 + pad 弹性填洞
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-snapshot-table-lifecycle-filter-semantics
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 写时共享/引用计数间接 extent 的一致性维护场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/reflink.c 在仓库中存在且含 trans_trigger_reflink_p_segment 定义
  evidence_level: unclassified
- name: constraints
  desc: 触发器计分的前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认重叠碎片计分、间接快照 options、pad 吸收错位三条前提在引用代码中有对应实现
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# reflink 触发器计分 + 归零自删

沉淀自 T0490（纵深分析）。对照 bcachefs `fs/data/reflink.c`、
`fs/data/write.c:485-554 DOC`。

## 核心概念

1. **触发器计分代替显式引用管理**：对重叠 `reflink_v` 碎片
   `+1/-1`；`refcount==0` 且 insert 时改 `KEY_TYPE_deleted`
   并清 TRIGGER_insert，级联释放空间/删 backpointer
   （`trans_trigger_reflink_p_segment`、`check_indirect_
   extent_deleting`）。上层覆写走普通 overwrite 触发器自动
   减数，无需特判。
2. **front/back_pad 弹性填洞**：insert 时撑大 pad，新旧切分缝隙
   只调 pad 不报错；lookup 区间含 pad，missing 以 live/refd 双
   区间区分真缺失。用 pad 吸收 split/合并错位，避免合并扫全
   事务（`bch2_lookup_indirect_extent`）。
3. **间接 extent 快照 inode options**：直接 extent 无 reconcile
   条目可从 inode 重推，间接后无属主，故创建时把
   compress/checksum/replicas/target 快照进 `reflink_v`
   （`bch2_make_extent_indirect:493-534`），跨文件传播受
   MAY_UPDATE_OPTIONS 控防越权降副本。

## 复用指南

- 引用计数优先用事务触发器自动计分，而非调用方手动 inc/dec。
- 区间索引的切分错位用弹性 pad 吸收，而非报错或全量重整。
- 间接化时把"原来可推导、间接后不可推导"的属性快照进间接
  条目。
