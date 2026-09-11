---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-fidelity-generic
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 验证信号必须指向观测
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-rule-attr-testable
---

# 验证信号必须指向观测

要求具体对象、判断方法和失败判据。多写“运行”“检查”“grep”并不自动让信号有效；字段存在与测试真实行为是不同层。不能引用缺失脚本当作已验证。
