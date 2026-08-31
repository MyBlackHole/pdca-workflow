---
schema: pdca.asset/v1
id: ontology:concept/trigger-condition
type: concept
layer: Knowledge
status: active
summary: 触发条件：user-invoked 和 model-invoked 技能的形式化触发机制
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/router-skill
attributes:
- name: applicability
  desc: 适用于所有技能的触发条件建模
  constraint: 见正文
  testable_signal: 检查每个技能是否声明触发短语和触发条件
- name: trigger_phrase
  desc: 触发短语（如 'Use when...'），用于招募模型先验
  constraint: 至少声明一个触发短语
  testable_signal: 检查技能描述是否包含声明式触发短语
- name: trigger_context
  desc: 触发条件（场景、上下文），定义技能何时被激活
  constraint: 见正文
  testable_signal: 检查触发条件是否覆盖所有预期场景
---

# Trigger Condition（触发条件）

user-invoked 和 model-invoked 技能的形式化触发机制。

## 触发短语（trigger_phrase）

用声明式短语定义技能的触发方式，招募模型先验：

- 格式：`Use when <场景>` 或 `<动词> when <条件>`
- 前置首词：触发短语靠首词做触发工作
- 一分支一触发词：同义改写 = 同一分支写两遍，收拢

## 触发条件（trigger_context）

定义技能何时被激活的上下文条件：

- 场景条件：任务类型、领域、复杂度
- 上下文条件：前置技能是否完成、输入是否就绪
- 依赖条件：其他技能或资源是否可用

## 原则

- 每个技能必须同时声明触发短语和触发条件
- 触发短语用于模型调用时的匹配，触发条件用于流程路由时的判断
- 触发条件变化时需更新 relations 中的依赖关系
- 触发条件由 `router-skill`（ask-matt）统一管理