---
schema: pdca.asset/v2
id: ontology:concept/handoff
type: concept
layer: Knowledge
summary: 交接：将当前对话紧凑地压缩为交接文档，使另一个 agent 可以继续工作
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/handoff/3.1.0
relations:
  specializes:
  - ontology:principle
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Handoff

交接：将当前对话紧凑地压缩为交接文档，使另一个 agent 可以继续工作。

- **含义**：将当前对话的关键信息、决策、待办压缩为一个紧凑的交接文档，供另一个 agent 在后续会话中继续工作。
- **关键不变量**：交接文档应包含上下文、决策、待办和下一步行动。

## 决策背景
- 背景：agent 会话之间缺乏状态传递机制，导致每次新会话都需要重新理解上下文。
- 决策：定义交接文档格式，使 agent 可以在会话之间传递状态。
