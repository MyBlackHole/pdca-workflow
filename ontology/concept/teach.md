---
schema: pdca.asset/v1
id: ontology:concept/teach
type: concept
layer: Knowledge
status: active
summary: 教学技能：多会话教授新技能或概念
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/trigger-condition
attributes:
- name: applicability
  desc: 适用于需要多会话教授新技能或概念的场景
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

# Teach（教学技能）

多会话教授新技能或概念。

## 原则

- teach 以当前目录为状态化教学工作区
- 跨多个会话逐步教授新技能或概念
- 每会话有明确的教学目标和完成标准
- 教学结果可沉淀为 Knowledge/Skill 资产