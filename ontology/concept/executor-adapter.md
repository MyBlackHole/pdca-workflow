---
schema: pdca.asset/v2
id: ontology:concept/executor-adapter
type: concept
semantic_kind: class
layer: Knowledge
status: deprecated
authority: reference
revision: 3.1.0
summary: 已退役：executor-adapter
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/capability-protocol
replaced_by: ontology:concept/capability-protocol
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 已退役：executor-adapter

原平台Registry/Adapter实现边界不再属于本项目；直接使用宿主原生能力。

旧ID仅作迁移定位，不能用作活动执行规则。现行权威：ontology:concept/capability-protocol。
