---
schema: pdca.asset/v1
id: ontology:concept/pdca-gate
type: concept
layer: Knowledge
summary: PDCA 阶段准入门禁元概念
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-gate

阶段准入门禁元概念。每个 phase 有其 `pdca-gate-<phase>` 节点，经 `relations.relates_to` 声明进入该 phase 必须满足的前置条件。

- **理由**：把"什么条件下才能进入某阶段"从分散的口头约定提升为机器可校验的本体关系，避免跳阶段或证据不全就推进。
- **驱动**：`ontology_reason.admission_conditions(phase)` 读取 `pdca-gate-<phase>.relates_to` 产出准入条件列表；元本体缺失时回退到硬编码最小核心。

