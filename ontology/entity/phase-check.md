---
schema: pdca.asset/v2
id: ontology:entity/phase-check
type: entity
semantic_kind: individual
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 阶段值：check
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/pdca-phase
  relates_to:
  - ontology:concept/pdca-phase-status
phase_value: check
state_kind: method_phase
---

# 阶段值：check

这是`pdca-phase`的具名阶段值。字段编码及终态含义由`pdca-phase-status`定义。

动作协议为 ontology:process/flow-check；准入/退出以GATE-01和TRANSITION-01为准。
