---
schema: pdca.asset/v2
id: ontology:domain/ai-efficiency-ai-execution-and-invocation-contracts
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 执行与调用契约
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge.ai-efficiency.ai-execution-and-invocation-contracts
source_ids:
- R0161
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

# 执行与调用契约

局部技能只能执行当前任务契约允许的动作；入口、输入、输出和失败路径清楚才能减少反复猜测。调用工具成功不等于业务验收通过。
