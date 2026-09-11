---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-guides-range
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 关系的类与实例范围
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/ontology-rule
  relates_to:
  - ontology:concept/ontology-asset
rule_spec: {}
---

# 关系的类与实例范围

specializes的两端必须为class，instance_of源为individual且目标为class。guides源为知识实例或知识类，目标为确实受其指导的实体/过程/主题，不能仅按目录猜语义。configured_by目标须是当前领域声明的配置节点；通用规则不限定TLSConfiguration。
