---
schema: pdca.asset/v1
id: ontology:concept/wizard
type: concept
layer: Knowledge
status: active
summary: 向导技能：交互式 bash 向导，引导用户完成步骤
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/trigger-condition
attributes:
- name: applicability
  desc: 适用于需要逐步引导用户完成交互式任务的场景
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

# Wizard（向导技能）

交互式 bash 向导，引导用户完成步骤。

## 原则

- wizard 生成交互式 bash 脚本，引导用户逐步完成
- 适用于配置基础设施、设置凭证、配置 CI 等场景
- 每个步骤有明确的完成标准
- 完成后输出可复用的配置结果