---
schema: pdca.asset/v2
id: ontology:domain/skill-verify-convergence
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 约束、案例、实现和证据逐项收敛
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/task-unit-test
  - ontology:process/independent-work-review
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 约束、案例、实现和证据逐项收敛

核验constraint→case→run→artifact的实际关联；TEST-01全必需案例对当前交付版本通过才支持confirmed。映射完整不等于业务通过；错误实现killed与正确实现pass分离。独立审查还按REVIEW-01核对反向覆盖和subject_conformance。
