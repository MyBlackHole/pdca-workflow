---
schema: pdca.asset/v2
id: ontology:entity/phase-archive
type: entity
semantic_kind: individual
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 工作流正常归档终态，不属于方法阶段
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/workflow-state
  relates_to:
  - ontology:concept/pdca-phase-status
phase_value: archive
state_kind: terminal
---

# 工作流终态：archive

这是workflow-state的终态实例，不是pdca-phase实例，也不是第五个PDCA方法阶段。保留稳定ID和phase_value=archive，兼容旧任务记录中的phase编码。

STATE-01要求archive与completed双向匹配并具备四条正常转换回执。异常终止保留原方法phase，用execution_state=interrupted，不能直接跳到archive。归档材料只读；完整性问题记录在独立报告中，不重开旧任务。
