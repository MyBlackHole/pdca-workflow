---
schema: pdca.asset/v2
id: ontology:concept/pdca-phase
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: PDCA 方法阶段
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/workflow-state
  relates_to:
  - ontology:concept/pdca-phase-status
  - ontology:concept/pdca-transition
  - ontology:process/pdca-flow-model
---

# PDCA 方法阶段

Plan 建立目标、预测、边界和验收；Do 按确认的契约开展工作；Check 用观测检验目标与预测；Act 处置结果和可复用认识。

状态编码只在 `pdca-phase-status` 定义。每阶段动作读取对应 `flow-*`，合法转换读取 `pdca-transition`，不得根据文件名自行发明阶段。

本类特化workflow-state，仅四个方法阶段实例；archive直接属于workflow-state而非本类。阶段动作仍按四个flow节点，查询时不可把终态混为方法阶段。
