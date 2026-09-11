---
schema: pdca.asset/v2
id: ontology:domain/workflow-skill-invocation-convention
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 技能不取得流程控制权
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge:workflow.skill-invocation-convention
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

# 技能不取得流程控制权

局部技能是当前阶段内动作，不得代签用户确认、直接改phase或发布新门禁。统一按契约选择动作，失败回报事实而不是编造执行回执。
