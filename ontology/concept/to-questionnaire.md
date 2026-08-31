---
schema: pdca.asset/v1
id: ontology:concept/to-questionnaire
type: concept
layer: Knowledge
status: active
summary: 问卷技能：将决策转化为 Markdown 问卷
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/trigger-condition
attributes:
- name: applicability
  desc: 适用于将无法单独回答的决策转化为问卷的场景
  constraint: 见正文
  testable_signal: 检查技能是否声明触发短语和触发条件
- name: trigger_phrase
  desc: 触发短语
  constraint: 至少声明一个
  testable_signal: 检查是否包含声明式触发短语
- name: trigger_context
  desc: 触发条件
  constraint: 见正文
  testable_signal: 检查触发条件是否覆盖所有预期场景
---

# To Questionnaire（问卷技能）

将决策转化为 Markdown 问卷。

## 原则

- 将无法单独回答的决策转化为 Markdown 问卷
- 问卷发送给能回答的人（异步或会议）
- 聚焦于发送者（谁、需要什么回），而非主题
- 问卷结果可回链到 decision 节点