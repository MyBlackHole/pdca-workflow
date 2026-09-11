---
schema: pdca.asset/v2
id: ontology:pattern/ontology-modular-reference
type: pattern
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 模块化本体引用
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:pattern
  relates_to:
  - ontology:concept/ontology-creation-gate
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-continuous-improvement
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 模块化本体引用

复用稳定ID，按适用性加载正文，关联不自动执行。将本体版本和内容摘要固定到当前任务，避免其他任务发布改变当前验收依据。
