---
schema: pdca.asset/v1
id: ontology:concept/model-invoked
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/model-invoked/1.0.0
summary: 模型调用技能：agent 可自主触发，常驻上下文负载
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/trigger-condition
attributes:
- name: applicability
  desc: 适用于所有模型可自主触发的技能
  constraint: 见正文
  testable_signal: 检查技能是否声明触发短语和触发条件
---

# Model Invoked

模型调用技能：agent 可自主触发，常驻上下文负载。

## 触发机制

- 触发短语：声明式短语（如 'Use when...'），模型匹配时触发
- 触发条件：场景和上下文条件满足时模型自主拉起
- 上下文负载：常载材料每轮 token 成本（无论是否触发都在花）

## 触发条件

- 由 `trigger-condition` 概念建模
- 触发短语用于模型调用时的匹配
- 触发条件用于流程路由时的判断
- 触发条件变化时需更新 relations 中的依赖关系
