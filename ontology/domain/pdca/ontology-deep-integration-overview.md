---
schema: pdca.asset/v2
id: ontology:domain/ontology-deep-integration-overview
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 本体驱动的集成视图
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

# 本体驱动的集成视图

集成链为权威语义→任务有界子图→执行步骤→产物→证据→结论。每个映射保持版本和来源，脚手架可生成不代表测试已执行。
