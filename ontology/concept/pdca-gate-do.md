---
schema: pdca.asset/v1
id: ontology:concept/pdca-gate-do
type: concept
layer: Knowledge
summary: do 阶段准入门禁：须满足 pdca-ontology-ready
status: active
relations:
  specializes:
  - ontology:concept/pdca-gate
  relates_to:
  - ontology:entity/phase-do
  - ontology:concept/pdca-ontology-ready
---
# pdca-gate-do

do 阶段准入门禁：声明进入 do 须满足 `pdca-ontology-ready`（由 `relates_to` 引用）。

- **准入条件来源**：`ontology_reason.admission_conditions("do")` 读取本节点的 `relates_to`，实测返回 `["ontology-ready"]`。
- **适用范围**：对所有 `scenario_type`（development/bugfix/research/design/review/documentation）在 `phase=do` 时均生效，确保本体成为所有工作的默认基础；仅显式 `ontology_exempt=true` 可豁免（须说明原因）。
- **理由**：执行前必须确认本任务的领域本体片段已声明且结构合法，或明确豁免，否则执行无语义锚点、产物易成孤儿资产。

