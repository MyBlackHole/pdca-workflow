---
schema: pdca.asset/v2
id: ontology:concept/pdca-home
type: concept
semantic_kind: class
layer: Knowledge
status: deprecated
authority: reference
revision: 3.1.0
summary: 已退役：pdca-home
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-record-identity
replaced_by: ontology:concept/task-record-identity
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 已退役：pdca-home

不再依赖全局PDCA_HOME或外部初始化脚本。入口使用明确项目根和授权路径，不自动注入目标项目。

旧ID仅作迁移定位，不能用作活动执行规则。现行权威：ontology:concept/task-record-identity。
