---
schema: pdca.asset/v1
id: ontology:concept/timeline-integrity-gate
type: concept
layer: Knowledge
status: active
summary: PDCA 流程文件时间线一致性护栏（确认时间真实、states 单调、receipt 唯一推进、先干后补确认违规）
relations:
  specializes:
  - ontology:concept/pdca-transition
  relates_to:
  - ontology:concept/pdca-transition
---

# 时间线一致性护栏（timeline-integrity-gate）

## 结论

AI 代理执行 PDCA 时，流程文件的时间戳与确认顺序必须可验证，违者 fail-closed 或由 doctor 体检标记。

## 规则

1. **确认时间必须真实**：`final_confirmation.at` 必须取自执行时刻（`date` 命令），禁止编造或预估未来时间（`FINAL_CONFIRMATION_AFTER_TRANSITION` / `CONFIRMATION_AFTER_PLAN_TO_DO`）。
2. **states 时间必须单调**：`created ≤ plan ≤ do ≤ check ≤ act ≤ archive`，回填乱序被 `STATE_TIME_ORDER` 检出。
3. **receipt 是唯一推进证据**：阶段转换只通过 `transition-phase.py`，`receipt.at` 须等于 `states.<target>`，否则 `RECEIPT_STATE_MISMATCH`。
4. **转换时刻语义**：plan→do 时门禁以"转换执行时刻"为界校验确认时间——确认可早于或等于转换，绝不可晚于。
5. **先干后补确认=违规**：Do 工作（implement.jsonl、产物提交）不得早于 final_confirmation；已被门禁与体检双重覆盖。
6. **plan 时间戳自动补写（T0239）**：任务初始 `states.plan=null`，plan→do 由 `transition-phase.py` 自动补写——优先取 `clarifications.jsonl` 的 `final_confirmation.at`；无 confirmation 时兜底用转换时刻（防御分支，真实 flow 中 `FINAL_CONFIRMATION_MISSING` 先拒）。

## 检查入口

- 转换时：`transition-phase.py`（fail-closed）
- 存量体检：`pdca-doctor.py --json` 的 `task_timeline` 段（非阻断）
- 违规登记：`report-flow-issue.py`（不可变 occurrence）

## 已知缺陷

- `meta.convergence` 允许 record ID 占位符（T0164 案例，issue CONVERGENCE_PLACEHOLDER，用户决策不修 schema）。
- 无 confirmation 时的 plan 兜底分支在真实 flow 中不可达。

## 来源

- `（原知识层）timeline-integrity-gates.md`
