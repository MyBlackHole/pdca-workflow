---
schema: pdca.asset/v1
id: ontology:concept/pdca-transition
type: concept
layer: Knowledge
summary: PDCA 阶段转换元概念（合法 phase→phase）
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-transition

PDCA 阶段转换元概念：描述"哪些 phase→phase 推进是合法的"。

- **编码方式**：每条合法转换是一个 `transition-*.md` 实体节点，`specializes: pdca-transition`，并通过 `relations.composed_of: [phase-<源>, phase-<的>]` 声明其首尾阶段。`ontology_reason.legal_transition(src, dst)` 与 `transition_targets(src)` 据此推理。
- **当前合法边**（任务生命周期）：`plan→do`、`do→check`、`check→act`、`act→archive`。
- **转换登记表**：`ontology/entity/transition-*.md`（如 `transition-plan-do.md` 等）。新增合法边须同步新增对应 `transition-*.md` 节点，否则 `ontology-validate` 与 `ontology_reason` 不会识别。
- **为何 act→plan 不是 transition 边**：方法论上 PDCA 是循环（act 之后回到 plan），但本工作流把单任务生命周期建模为**有终点的流水线**（act→archive），且 `ontology-validate` 要求转换图**无环**（见 `test_ac2_no_cycle_dangling`）。因此"act→plan 循环"以**概念关系**表达（`ontology:concept/pdca-continuous-improvement` 的 `relates_to: [phase-act, phase-plan]`），而非可执行的 transition 边。若未来需要把 act→plan 设为合法任务转换，须同时将其加入 `ontology-validate` 的白名单。
- **推进约束**：阶段只能经 `scripts/transition-phase.py` 按合法边推进，且须通过门禁校验（`pdca-task` 的不变量）。

