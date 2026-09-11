---
schema: pdca.asset/v2
id: ontology:entity/transition-do-check
type: entity
semantic_kind: individual
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 转换：do → check
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/pdca-transition
  relates_to:
  - ontology:entity/phase-do
  - ontology:entity/phase-check
  - ontology:concept/pdca-gate
transition_spec:
  from: do
  to: check
  gate_id: do_to_check
  sequence: 2
---

# 转换：do → check

仅定义边和门禁标识。具体准入由GATE-01、提交/恢复由TRANSITION-01与RECOVERY-01定义；不按列表顺序推断首尾。

固定sequence=2，唯一键为(task_id,sequence)。取消事件不占用编号；合法提交和恢复只依TRANSITION-01。
