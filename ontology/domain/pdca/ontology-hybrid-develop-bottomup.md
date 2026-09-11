---
schema: pdca.asset/v2
id: ontology:domain/ontology-hybrid-develop-bottomup
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 从叶到根的实现
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-feedback
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 从叶到根的实现

先实现具有清晰输入输出和可验证边界的叶模块，再按直接依赖集成。共享状态、资源冲突和错误传播必须在集成验证中覆盖；没有实际回归不能声称逐批保绿。
