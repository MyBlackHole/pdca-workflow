# 投射 ontology:concept/pdca-task 独立任务门禁

## 问题陈述

T2178 已取得用户最终开工确认，但 `plan → do` 被 `TICKETS_MISSING` 拒绝，因为 runtime 仍要求无 parent 的任务必须拥有 child ticket。该门禁把任务拆解关系错误地用作生命周期准入条件，与 `ontology:concept/pdca-task` 已确认的“每个 PDCA 独立完整、parent/dependencies 仅用于调度”不变量冲突。

## 目标

把独立 PDCA 语义最小投射到 Plan→Do 门禁：任务是否有 parent 或 children 不影响阶段转换；任务拆解仍是可选规划能力，但不再是执行准入条件。

## 范围

- 删除 Plan→Do 中 `TICKETS_MISSING` 的 parent/children 强制门禁。
- 更新对应门禁测试，覆盖无 parent、无 children 的三个专业职责任务均可独立进入 Do。
- 保持 final confirmation、Grill、PRD、本体就绪和其他门禁不变。

## 范围外

- 旧六场景、A/B/C 和场景边界本体清理，由 T2178 承担。
- `agent.spawn`、协调挂起及恢复机制的完整 runtime 投射。
- 改写 parent、children 或 dependencies 的数据结构。

## 验收标准

- [ ] AC-1（回链 T2178 阻断）: 无 parent 且无 children 的独立 PDCA，在其他 Plan 门禁满足时不再产生 `TICKETS_MISSING`。
- [ ] AC-2（回链 T2178 AC-3）: parent、children 和 dependencies 仅保留拆分与调度语义，不参与 Plan→Do 生命周期准入。
- [ ] AC-3（回链 T2178 AC-4）: `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification` 三种职责均有无 children 独立执行回归覆盖。
- [ ] AC-4（回链 T2178 AC-8）: final confirmation、Grill、PRD、本体就绪及相邻阶段转换门禁的既有测试继续通过。
- [ ] AC-5（回链 T2178 AC-7）: runtime 不再包含 `TICKETS_MISSING`、`non-research tasks require at least one child ticket` 或 parent 叶豁免控制分支。

### 声明的测试接缝

- seam: `tests/test_tickets_gate.py` -> `scripts/pdca_core.py::gate_issues`
- seam: `tests/test_gate_negative.py` -> `scripts/transition-phase.py`

## 关联本体节点

- `ontology:concept/pdca-task`
- `ontology:concept/pdca-gate-do`
- `ontology:domain/skill-to-tickets`

## 拆分映射

- 独立任务准入投射 -> `ontology:concept/pdca-task`
