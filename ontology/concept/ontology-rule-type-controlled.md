---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-type-controlled
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 类型与目录分组一致
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/ontology-rule
  relates_to:
  - ontology:concept/ontology-asset
rule_spec:
  allowed_types:
  - domain
  - entity
  - concept
  - process
  - role
  - pattern
  - principle
  - pitfall
  - fact
  - decision
  directory_rule: first_segment_under_ontology
---

# 类型与目录分组一致

检查type属于受控词表，且等于ontology下第一层目录名；嵌套子目录只是定位，不是type。ID唯一，semantic_kind必须显式。
