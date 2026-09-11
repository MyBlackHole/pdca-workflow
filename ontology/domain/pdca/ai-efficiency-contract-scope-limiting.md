---
schema: pdca.asset/v2
id: ontology:domain/ai-efficiency-contract-scope-limiting
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 限制契约范围
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge.ai-efficiency.contract-scope-limiting
source_ids:
- T0238-0809-mechanism-fixes
- T0234-0809-fastapi-app-verify
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

# 限制契约范围

固定in-scope/out-of-scope、必需动作和验收后再实施；工具可做的事情不自动成为该任务该做的事情。偏差必须显式处置。
