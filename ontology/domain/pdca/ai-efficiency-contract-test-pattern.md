---
schema: pdca.asset/v2
id: ontology:domain/ai-efficiency-contract-test-pattern
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 契约测试对比真实实现
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge.ai-efficiency.contract-test-pattern
source_ids:
- T0233-0809-seam-contract
- T0231-0809-followup-frontier-batch-spread
- T0232-0809-ticket-dag-design-twice
- T0240-0809-seam-ci-gate
- T0241-0809-seam-doctor-gate
- T0244-0809-pdca-flow-impl-review
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

# 契约测试对比真实实现

测试应对比声明的输入/输出/行为与实际实现，不仅检查文档提到了关键词。区分缺失、不一致、不适用和通过；独立输入应能触发反例失败。
