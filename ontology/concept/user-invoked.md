---
schema: pdca.asset/v1
id: ontology:concept/user-invoked
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/user-invoked/1.0.0
summary: 用户调用技能：仅用户手动触发，零上下文负载
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/trigger-condition
attributes:
- name: applicability
  desc: 适用于所有用户手动触发的技能
  constraint: 见正文
  testable_signal: 检查技能是否声明触发短语和触发条件
---

# User Invoked

用户调用技能：仅用户手动触发，零上下文负载。

## 触发机制

- 触发短语：用户输入匹配时触发（如 `/grill`、`/triage`）
- 触发条件：用户主动调用，不依赖模型自主判断
- 上下文负载：零（仅触发时消耗）

## 触发条件

- 由 `trigger-condition` 概念建模
- 触发短语前置首词做触发工作
- 一分支一触发词
