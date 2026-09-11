---
schema: pdca.asset/v2
id: ontology:concept/triage-state-machine
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 需求分诊不是额外生命周期
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-phase-status
  - ontology:process/flow-plan
---

# 需求分诊不是额外生命周期

分诊在Plan中完成：识别目标、职责、契约和必须澄清的问题。用户已给答案直接引用；有实质未知才提问。无需固定P1-P6阶段或强制追问轮数，正式phase由状态规范定义。
