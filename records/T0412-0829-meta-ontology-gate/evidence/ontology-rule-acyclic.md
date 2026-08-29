---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-acyclic
type: concept
layer: Knowledge
summary: AC-3 specializes 形成以 Entity 为根的无环图
status: active
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-acyclic

**AC-3（关系无环）**：`specializes` 必须形成以 `Entity` 为根的有向无环树；所有关系图（含 `composed_of`）无环。

- 对应 `ontology-validate.py` 的 AC-3 实现（CYCLE）。
- 违反示例：`A specializes B` 且 `B specializes A`。
