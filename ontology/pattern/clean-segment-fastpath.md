---
schema: pdca.asset/v2
id: ontology:pattern/clean-segment-fastpath
type: pattern
layer: Knowledge
status: active
summary: clean段加速加校验回退模式
source_task: T0506
relations:
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:domain/core-superblock-readback-validation
  instance_of:
  - ontology:pattern
attributes:
- name: applicability
  desc: 干净关闭加速挂载、加速结构可信校验场景
  constraint: ''
  testable_signal: 抽查源节点 core-superblock-readback-validation 存在
  evidence_level: unclassified
- name: consequences
  desc: 干净挂载秒开、校验失败全量回退、写入成本略增
  constraint: ''
  testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
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

# clean 段加速加校验回退

来源：T0506 提炼；源节点 `core-journal-seq-blacklist-pin-reclaim`、
`core-superblock-readback-validation`；对照 bcachefs
`fs/sb/clean.c`。

## 问题

每次挂载全量回放日志太慢；但加速结构不可信则 corrupt。

## 方案

干净关闭把树根用量时钟打包进 clean 段；下次比对序号与树根，
一致跳过回放，不一致丢弃强制走日志。

## 后果

干净挂载秒开；校验失败全量回退保证正确；代价是关机多写一段；
clean 段是纯加速，绝不能是唯一真相源。
