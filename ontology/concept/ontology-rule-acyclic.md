---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-acyclic
type: concept
layer: Knowledge
summary: AC-3 引用图无环（relations 构成的图须为 DAG）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-rule-acyclic/1.0.0
rule_spec:
  graph_relation_keys:
  - specializes
  - instance_of
  - composed_of
  - configured_by
  - part_of
  - guides
  - relates_to
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-acyclic

**AC-3（关系无环）**：`specializes` 必须形成以 `Entity` 为根的有向无环树；所有关系图（含 `composed_of`）无环。

- 对应 `ontology-validate.py` 的 AC-3 实现（CYCLE）。
- 违反示例：`A specializes B` 且 `B specializes A`。
