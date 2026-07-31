# PDCA 流程文件时间线一致性护栏

## 结论

✅ AI 代理执行 PDCA 时，流程文件的时间戳与确认顺序必须可验证，违者 fail-closed 或由 doctor 体检标记。

## 规则

1. **确认时间必须真实**：`final_confirmation` 的 `at` 必须取自执行时刻（`date` 命令），禁止编造或预估未来时间。违反表现为 `FINAL_CONFIRMATION_AFTER_TRANSITION`（转换时）或 `CONFIRMATION_AFTER_PLAN_TO_DO`（doctor 体检）。
2. **states 时间必须单调**：`created ≤ plan ≤ do ≤ check ≤ act ≤ archive`，任何回填导致乱序都会被 `STATE_TIME_ORDER` 检出。
3. **receipt 是唯一推进证据**：阶段转换只通过 `transition-phase.py`，receipt.at 必须等于 `states.<target>`，否则 `RECEIPT_STATE_MISMATCH`。
4. **转换时刻的语义**：plan→do 时门禁以"转换执行时刻"为界校验确认时间——确认可以早于或等于转换，但绝不可晚于转换。
5. **先干活后补确认=违规**：Do 工作（implement.jsonl 记录、产物提交）不得早于 final_confirmation；此类模式已被门禁与体检双重覆盖。

## 检查入口

- 转换时：`transition-phase.py`（fail-closed，issue code 含修复指引）
- 存量体检：`pdca-doctor.py --json` 的 `task_timeline` 段（非阻断）
- 违规登记：`report-flow-issue.py`（不可变 occurrence）

## 已知缺陷

- `meta.convergence` 允许 record ID 占位符（T0164 案例，issue CONVERGENCE_PLACEHOLDER，用户决策不修 schema）。
