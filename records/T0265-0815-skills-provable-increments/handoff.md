# T0265 Handoff — 落地 mattpocock/skills 三个可证明增量

## 当前状态

T0265（AGENT-BRIEF 模板 / wide-refactor 保绿序列化 / ticket claim 并发防冲突）已完成并确认 verdict=confirmed，进入归档。

- `skills/triage-work/SKILL.md`：新增 AGENT-BRIEF 11 字段模板（category/scenario_type/summary/current/desired/key interfaces/acceptance criteria/out of scope/information gaps/dedup results/recommended next steps）+ 可检查质量约束（AC 可测性、durability over precision 禁 `:line`/文件路径、ready-to-plan 必带 brief）+ grep 检查命令。
- `skills/to-tickets/SKILL.md`：新增 wide-refactor 分支（expand→分批迁移→contract→integrate），含 blast radius 判定、依赖边声明、逐批 CI 绿 100% 硬指标、expand 阶段旧形式契约测试说明。**推翻 `records/T0232-0809-ticket-dag-design-twice` 的 expand-contract 不落地决定**。
- `skills/wayfinding-work/SKILL.md`：新增 ticket claim 机制（claimed-by/in-progress、unclaimed 票可选、并发跳过、resolve 清除）+ 状态机说明。
- `scripts/check-ticket-claims.py`：claim/resolve/status 状态机，状态写 `tickets/claims.jsonl`，`--tickets` 支持自定义路径。
- `tests/test_skills_increments.py`：10 测试（6 结构契约 + 4 状态机行为）全绿。
- evidence 已登记（AC-1..AC-8，9 条）、convergence-map 已固定（v2，valid: True）、conclusion.md 已写、check_confirmation=confirmed、verdict=T0265-vd-001。

## 未完成事项

1. **AGENT-BRIEF 质量约束接入自动门禁**：grep 检查命令目前是 skill 指引性检查，未在 triage 产出时自动拦截。
2. **claim 状态机进程级锁**：当前轻量文件事件日志，无集中式锁；极端并发依赖 POSIX append 原子性。
3. **wide-refactor 逐批 CI 绿脚本化**：skill 文档为说明性指标，未落地为 scripts/ 下的可运行验证脚本。
4. **测试未跟踪的 skills/ 检查**：`test_generated_index_is_current` 需确认三 skill 改动后 SKILLS-INDEX 是否同步。

## 已知约束

- 4 个全量测试失败均为既有状态：2 harness（`test_all_deterministic_fixtures_pass`、`test_public_harness_runs_real_lifecycle_success_and_transition_failures`）+ 2 doctor（`test_doctor_uses_explicit_fallbacks`、`test_doctor_reports_seam_contracts_segment`）；均因 round62-67 外部任务缺失，`git stash` 隔离验证非本任务回归。
- LSP 静态告警（`arch_review`/`pdca_core` import 无法解析）不影响运行时。
- claim 状态机写 `tickets/claims.jsonl`（仓库根），测试用 `--tickets` 参数隔离到临时目录；此前误写仓库根 `tickets/` 已删除。

## 推荐的下一步

1. 将 AGENT-BRIEF 质量约束接入自动门禁（triage 产出时运行 grep 检查，缺 brief 或含文件路径时拦截）。
2. 为 `check-ticket-claims.py` 增加进程级文件锁。
3. 把 wide-refactor 逐批 CI 绿做成可运行脚本（记录每批提交 → 校验每批测试通过 → 输出绿比例）。
4. T0263（identity 观察）继续挂起等待观察窗，观察期满后出 effectiveness verdict。

## 关键上下文文件列表

- `pdca/tasks/0815-skills-provable-increments/`：prd.md、task.json、clarifications.jsonl、implement.jsonl
- `records/T0265-0815-skills-provable-increments/conclusion.md`、`evidence/`（含 convergence-v2.json）
- `skills/triage-work/SKILL.md`、`skills/to-tickets/SKILL.md`、`skills/wayfinding-work/SKILL.md`
- `scripts/check-ticket-claims.py`
- `tests/test_skills_increments.py`
- `records/T0232-0809-ticket-dag-design-twice/conclusion.md`（被推翻的 expand-contract 决策）

## Suggested Skills

- 接入 AGENT-BRIEF 自动门禁：`testing-strategy`、`code-review-checklist`
- claim 状态机加锁：`memory-model-concurrency`
- 逐批 CI 绿脚本：`testing-strategy`、`build-config`
