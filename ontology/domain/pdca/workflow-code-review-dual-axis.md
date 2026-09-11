---
schema: pdca.asset/v2
id: ontology:domain/workflow-code-review-dual-axis
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 审查的行为与工程两轴
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge:workflow.code-review-dual-axis
source_ids: []
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

# 审查的行为与工程两轴

行为轴检查是否满足契约与失败语义；工程轴检查接口、所有权、并发、兼容性和验证。两轴发现都需具名位置、条件和证据。
