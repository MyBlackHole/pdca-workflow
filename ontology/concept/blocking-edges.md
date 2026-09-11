---
schema: pdca.asset/v2
id: ontology:concept/blocking-edges
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 组成树之外的明确输入依赖
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-tree-scheduling
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-dependency-graph
  - ontology:concept/resource-ownership
---

# 组成边与输入前置不能混淆

工作目标树父边表示组成，实际输入depends_on表示producer→consumer的前置。检查时机、图身份、合并与查环唯一权威为DEPENDENCY-01，运行就绪为SCHED-01；本节点不维护第二份算法。

projection检查孩子实现→父实现与额外输入的并集；modeling父seed→孩子是不同scene的顶点，不混成假环。relates_to/guides只作检索线索，不能产生调度边。

兄弟不天然可安全并行，资源按RESOURCE-01。局部可用固定替身测试接口，但最终组合必须引用真实孩子固定交付。环、缺生产者或陈旧检查回执使候选阻断，不删除义务伪造ready。
