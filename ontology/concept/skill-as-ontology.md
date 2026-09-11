---
schema: pdca.asset/v2
id: ontology:concept/skill-as-ontology
type: concept
layer: Knowledge
status: active
revision: 3.4.6
semantic_kind: class
summary: 技能知识定义、调用契约与运行证据的分工；不引入独立生命周期
relations:
  specializes:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/skill-mechanics
  - ontology:concept/skill-invocation-contract
authority: reference
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Skill 作为知识定义

Skill 定义是一份可检索、组合和按适用条件采用的知识资产；不是某个 Agent 的配置，也不是一条已经执行的任务记录。

技能与流程分工以 [skill-mechanics](skill-mechanics.md) 为准；输入、输出、前置和失败处理以 [skill-invocation-contract](skill-invocation-contract.md) 为准。本页是解释性资料，不能授予写权、跳过确认或创设另一条生命周期。

定义固定在本体库；某次调用绑定任务、定义版本和实际工具；观测保留在该次 records。证据只支持它确实检查的主张与版本，不为整份 Skill 或其它调用背书。没有新知识时复用既有定义，不为一次调用重复造本体。
