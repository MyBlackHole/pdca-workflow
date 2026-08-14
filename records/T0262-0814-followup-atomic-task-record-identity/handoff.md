## 当前状态

T0262（统一 task/record identity 原子创建）已完成并确认 verdict=confirmed、disposition=projected，进入归档。

- 统一入口 `scripts/task_identity.py`：flock 仓库锁 + `_next_task_id` reservation + create-only + 失败回滚；CLI `create` 子命令。
- 收敛：triage、to-tickets、Act follow-up 统一走 `task_identity.py create`；promotion 复用 `_create_task_unlocked`。
- audit fail-closed：缺 record / 非法路径写 `records/__quarantine/flow-audit.json`，无 `task.id` fallback。
- 诊断：`identity_diagnostics` 增加 `record_derived_mismatches`；接入 `validate-workflow.py --all` 与 `pdca-doctor.py`。
- evidence 已登记（AC-1..AC-8）、convergence-map 已固定、conclusion.md 已写、check_confirmation=confirmed。

## 未完成事项

1. **AC-8 观察窗**：14 天或 20 个真实新任务后，以独立 follow-up 任务对照 T0261/T0262 baseline 出具 effectiveness verdict。
2. 20 条历史 `record_derived_mismatch`（旧 `R-` 约定）与 25 条 duplicate task IDs 的人工处置（batch 迁移或 alias receipt，未实施）。
3. `records/__quarantine/flow-audit.json` 既有事件的转正/废弃处置流程未定义。

## 已知约束

- 历史只诊断不改写（AC-6）；缺失 record 的历史任务不计入 conflict。
- doctor 全局 valid 不并入 identity（避免历史冲突永久 red）；`validate-workflow.py --all` 仍并入。
- `tests/test_operations.py` 两个 doctor 测试在真实仓库失败：9 个既有外部任务（round66/67）PRD seam 指向外部 C++ 测试文件。已 stash 基线验证为既有状态，非 T0262 回归。
- 老约定 record 前缀为 `R-{id}-{name}`，新约定 `T{id}-{slug}`。

## 推荐的下一步

1. 创建观察 follow-up 任务（必须经 `scripts/task_identity.py create`，验证统一入口在真实使用中的效果）。
2. 处置历史 record/duplicate 冲突（批量迁移或 relocation receipt 机制）。
3. 评估 `seam_contract.py` 是否忽略外部项目 seam，或隔离 doctor 环境假设。

## 关键上下文文件列表

- `pdca/tasks/0814-followup-atomic-task-record-identity/`：prd.md、task.json、clarifications.jsonl、convergence.json
- `records/T0262-0814-followup-atomic-task-record-identity/conclusion.md`
- `scripts/task_identity.py`、`scripts/flow_audit.py`、`scripts/flow_issues.py`、`scripts/pdca_core.py`
- `docs/adr/ADR-0024-atomic-task-record-identity.md`
- `knowledge/pdca-flow/task-record-identity-invariants.md`
- T0261 baseline：`records/T0261-0814-followup-task-record-identity/conclusion.md`

## Suggested Skills

- 下一轮 observe follow-up：`testing-strategy`（观察指标与配对统计）、`feature-commit-format`
- 若处理历史批量迁移：`code-review-checklist`、`secure-coding`（路径校验）