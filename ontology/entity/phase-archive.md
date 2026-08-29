---
schema: pdca.asset/v1
id: ontology:entity/phase-archive
type: entity
layer: Knowledge
summary: PDCA archive 阶段
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-archive

PDCA 的终态阶段（归档动作由 act 收尾触发，作为独立阶段节点存在）。

- **目的**：将完成任务移出活跃任务区，保留不可变记录。
- **进入条件**：act 收尾完成，`meta.disposition` 已设。
- **关键活动**：`advance-phase` 设 `phase=archive` + `active=false` → 二次提交 metadata → `mv` 任务目录到 `pdca/tasks/archive/YYYY-MM/`。
- **对应约定**：`flows/flow-act/SKILL.md` 的 Ac8。

