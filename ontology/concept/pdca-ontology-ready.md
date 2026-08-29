---
schema: pdca.asset/v1
id: ontology:concept/pdca-ontology-ready
type: concept
layer: Knowledge
summary: do 阶段准入门禁本体：任务领域本体片段须存在且 ontology-validate 通过
status: active
relations:
  specializes:
  - ontology:concept/pdca-gate
  relates_to:
  - ontology:entity/phase-do
---
# pdca-ontology-ready

do 阶段准入条件元概念（由 `pdca-gate-do.relates_to` 引用）。

- **含义**：进入 do 前，`meta.ontology_fragment` 指向的本体片段须存在且为合法 `pdca.asset/v1`（frontmatter + relations 通过 `ontology-validate`）；或 `meta.ontology_exempt=true` 豁免。
- **理由**：保证执行产物能挂接到本体图谱，避免产生无法被机器消费的"孤儿"资产。

