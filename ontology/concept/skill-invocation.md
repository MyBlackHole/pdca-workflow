---
schema: pdca.asset/v2
id: ontology:concept/skill-invocation
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
owl_versionIRI: http://pdca.local/ontology/skill-invocation/3.4.6
summary: 技能调用：基于 ontology 知识单元的调用机制
relations:
  specializes:
  - ontology:concept/skill-mechanics
revision: 3.4.6
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Skill Invocation

调用是在当前节点任务内，使用已固定技能定义完成一个获权动作；不是新建阶段、另起 Do-only 工作流或跳过真实确认。

流程和技能分工见 [skill-mechanics](skill-mechanics.md)，调用边界见 [skill-invocation-contract](skill-invocation-contract.md)。本文仅解释知识调用，不复制生命周期权威。调用输入、工具能力、实际观察与所用定义版本分别保留，既有 PASS 不能随定义跨任务复用。
