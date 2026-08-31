---
schema: pdca.asset/v1
id: ontology:entity/phase-archive
type: entity
layer: Knowledge
summary: 本工作流任务生命周期的运维扩展终态（非 PDCA 方法论阶段）
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-archive

**运维扩展终态**：归档动作由 `act` 收尾触发，作为独立节点存在。它**不是 PDCA 方法论的阶段**（PDCA 方法论只有 plan/do/check/act 四阶段，见 `ontology:concept/pdca-phase`）。

- **目的**：将已完成任务移出活跃任务区，保留不可变记录（本工作流单任务生命周期的终点）。
- **进入条件**：act 收尾完成，`meta.disposition` 已设。
- **关键活动**：`advance-phase` 设 `phase=archive` + `active=false` → 二次提交 metadata → `mv` 任务目录到 `pdca/tasks/archive/YYYY-MM/`。
- **与 PDCA 循环的关系**：方法论上的"下一轮 plan"由 `ontology:concept/pdca-continuous-improvement` 承载，而非由本节点回到 plan；本节点仅终止单任务。
- **对应约定**：`ontology/process/flow-{plan,do,check,act}.md` 的 Ac8。

