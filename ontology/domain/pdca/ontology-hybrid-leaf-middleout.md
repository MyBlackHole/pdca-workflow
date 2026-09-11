---
schema: pdca.asset/v2
id: ontology:domain/ontology-hybrid-leaf-middleout
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 局部切入的建模
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

# 局部切入的建模

从已知故障、接口或约束向上下游追踪必要关系，逐步补齐当前验收所需子图。不要把局部假设提升成全局规则。
