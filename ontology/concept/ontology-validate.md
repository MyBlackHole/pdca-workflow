---
schema: pdca.asset/v2
id: ontology:concept/ontology-validate
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 本体验证职责（无自带执行器）
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-creation-gate
---

# 本体验证职责（无自带执行器）

本节点保留原ID供引用迁移。当前验证流程统一为 `ontology:concept/ontology-creation-gate`；它定义实际要检查的对象和失败处理，而不是一个默认存在的CLI。宿主可以使用通用文件、YAML或图工具执行机械检查；未执行的行为用例必须明确标注。
