---
schema: pdca.asset/v1
id: ontology:concept/context-pointer
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/context-pointer/1.0.0
summary: 上下文指针：引用域外材料并编码触发条件的上下文指针
relations:
  specializes:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有写给 AI 消费的上下文指针
  constraint: 见正文
  testable_signal: 检查指针是否前置首词；同义分支是否收拢；常载指针是否修剪
- name: branch_trigger
  desc: 分支触发条件列表，定义指针在哪些分支下触发
  constraint: 见正文
  testable_signal: 检查每个分支是否有对应的触发条件
---

# Context Pointer

上下文指针：引用域外材料并编码触发条件的上下文指针
