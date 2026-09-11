---
schema: pdca.asset/v2
id: ontology:entity/phase-plan
type: entity
semantic_kind: individual
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 阶段值：plan
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/pdca-phase
  relates_to:
  - ontology:concept/pdca-phase-status
phase_value: plan
state_kind: method_phase
---

# 阶段值：plan

这是`pdca-phase`的具名阶段值。字段编码及终态含义由`pdca-phase-status`定义。

动作协议为 ontology:process/flow-plan；准入/退出以GATE-01和TRANSITION-01为准。
