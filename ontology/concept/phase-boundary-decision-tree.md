---
schema: pdca.asset/v2
id: ontology:concept/phase-boundary-decision-tree
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 阶段、场景与等待的边界
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-gate
  - ontology:concept/pdca-recovery
  - ontology:concept/task-rework
---

# 阶段、场景与等待的边界

先RECOVERY-01核验完整回执链，再按GATE-01判断当前任务的下一条边。scene不是phase；awaiting_confirmation/awaiting_input不是新增阶段。没有等待父审查放行的通用状态。

Do内有限修复不形成新PDCA；进入Check以后需要实现返工则原任务诚实处置，新attempt新Agent完整循环。第三场景审查不由任务内部Check递归派生。
