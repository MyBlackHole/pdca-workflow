---
schema: pdca.asset/v2
id: ontology:pattern/ontology-evaluation-oops
type: pattern
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 本体缺陷检查
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

# 本体缺陷检查

识别缺失引用、类/实例混用、过度继承、无关关系和不可验证约束。按关系语义检查循环；工具可辅助但不是默认依赖。缺陷严重度应解释对任务的实际影响。
