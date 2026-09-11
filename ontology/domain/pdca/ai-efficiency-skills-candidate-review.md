---
schema: pdca.asset/v2
id: ontology:domain/ai-efficiency-skills-candidate-review
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 技能候选审查
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge.ai-efficiency.skills-candidate-review
source_ids:
- T0242-0809-skills-candidates-review
- T0243-0809-diagnosing-bugs-enhance
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

# 技能候选审查

候选须解决具名执行问题，并提供适用边界、输入输出和验证方法。避免和现有权威重复；未在真实任务验证的候选不宣称提升成功率。
