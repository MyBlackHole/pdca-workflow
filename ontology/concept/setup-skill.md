---
schema: pdca.asset/v1
id: ontology:concept/setup-skill
type: concept
layer: Knowledge
status: active
summary: 设置技能：配置 repo 以使用技能库的模式
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/router-skill
attributes:
- name: applicability
  desc: 适用于所有需要配置 repo 以使用技能库的场景
  constraint: 见正文
  testable_signal: 检查技能是否声明其配置模式
- name: trigger_phrase
  desc: 触发短语
  constraint: 至少声明一个
  testable_signal: 检查是否包含声明式触发短语
- name: trigger_context
  desc: 触发条件
  constraint: 见正文
  testable_signal: 检查触发条件是否覆盖所有预期场景
---

# Setup Skill（设置技能）

配置 repo 以使用技能库的通用模式。

## 原则

- setup 技能在 repo 首次使用时运行一次
- 配置内容包括：issue tracker 选择、triage 标签、领域文档布局
- 配置结果持久化，后续技能可直接引用
- setup 完成后引导用户进入入口技能（如 ask-matt）