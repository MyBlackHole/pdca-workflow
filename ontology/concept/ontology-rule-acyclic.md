---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-acyclic
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 按关系语义检查循环
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/ontology-rule
  relates_to:
  - ontology:concept/ontology-asset
rule_spec:
  acyclic_relation_sets:
  - - specializes
  - - requires
    - depends_on
  part_graph: composed_of + reversed(part_of), deduplicated
  cycles_allowed:
  - relates_to
  - guides
---

# 按关系语义检查循环

分别检查specializes继承图、requires/depends_on执行依赖图和严格部分图无环。part_of反转为composed_of方向后去重；允许composed_of/part_of互逆表达同一事实。relates_to/guides可双向，不做全图DAG要求。A依赖B且B依赖A必须阻断，A相关B且B相关A允许。
