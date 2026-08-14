---
schema: pdca.asset/v1
id: T0265-0815-skills-provable-increments
phase: check
source_ids: [ac1-brief-template, ac2-brief-constraints, ac3-refactor-branch, ac4-refactor-metrics, ac5-claim-mechanism, ac6-claim-conflict, ac7-tests, ac8-no-regression, convergence-map-v2]
---

## 上下文

T0265 基于对 mattpocock/skills 的重新评估，落地三个此前缺失但可被硬指标证明价值的机制：① triage-work 的 AGENT-BRIEF 结构化模板与可检查质量约束；② to-tickets 的 wide-refactor 保绿序列化（expand→分批迁移→contract）；③ wayfinding-work 的 ticket claim 并发防冲突。三个增量均以文档结构契约测试 + 状态机行为测试作为可证明指标，与 T0264 的可证明指标方法论一脉相承。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：AGENT-BRIEF 模板可落地为 triage-work 的可检查产出 | **supported**：`triage-work/SKILL.md` 新增 11 字段模板（category/scenario_type/summary/current behavior/desired behavior/key interfaces/acceptance criteria/out of scope/information gaps/dedup results/recommended next steps）+ 质量约束（AC 可测性、durability over precision 禁 `:line`/文件路径、ready-to-plan 必带 brief）+ grep 检查命令。测试 `test_triage_work_*` 断言字段与约束存在。 |
| H2：wide-refactor 序列化可落地为 to-tickets 的分支 | **supported**：`to-tickets/SKILL.md` 新增 wide-refactor 分支（expand→分批迁移→contract→integrate），含 blast radius 判定、依赖边声明、逐批 CI 绿 100% 硬指标、expand 阶段旧形式契约测试说明。测试 `test_to_tickets_*` 断言所有标记。 |
| H3：ticket claim 状态机可防并发冲突 | **supported**：`wayfinding-work/SKILL.md` 新增 claim 步骤（claimed-by/in-progress、unclaimed 票可选、并发跳过、resolve 清除）；`scripts/check-ticket-claims.py` 实现 claim/resolve/status 状态机；测试 `TicketClaimStateMachineTest` 断言认领→解决循环、冲突拒绝（ALREADY_CLAIMED）、非认领者 resolve 拒绝（NOT_CLAIMANT）、解决后重新认领。 |
| H4：每个增量有可证明硬指标 | **supported**：`tests/test_skills_increments.py` 共 10 测试全绿（6 结构契约 + 4 状态机），含 seam 契约锚点 `skills/` 目录。 |
| H5：全量测试无回归 | **supported**：全量 201 passed / 4 failed / 13 subtests；4 个失败全部经 `git stash` 隔离验证为既有状态（2 harness AI-friendliness + 2 doctor seam 检查，均因 round62-67 外部任务缺失），非本任务回归。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 triage-work 含 AGENT-BRIEF 结构化模板（11 字段） | ac1-brief-template（SKILL.md 3829 字节，测试断言字段） | Passed |
| AC-2 模板含可检查质量约束 | ac2-brief-constraints（AC 可测性、durability over precision、ready-to-plan 必带 brief） | Passed |
| AC-3 to-tickets 含 wide-refactor 分支（expand→分批→contract→integrate） | ac3-refactor-branch（SKILL.md 4936 字节，测试断言标记） | Passed |
| AC-4 wide-refactor 含逐批 CI 绿硬指标与 expand 契约测试说明 | ac4-refactor-metrics（逐批 CI 绿 100%、旧形式契约测试） | Passed |
| AC-5 wayfinding-work 含 claim 机制 | ac5-claim-mechanism（claimed-by/in-progress/unclaimed/resolved，claim 在步骤 3 之前） | Passed |
| AC-6 claim 有冲突检测可证明性 | ac6-claim-conflict（check-ticket-claims.py 状态机，4 行为测试） | Passed |
| AC-7 tests/test_skills_increments.py 断言三 skill 结构契约，测试通过 | ac7-tests（10 passed） | Passed |
| AC-8 相关测试集通过无回归 | ac8-no-regression（201 passed，4 既有失败非回归） | Passed |

### 关键实现决策

- **测试先写**：先在 `tests/test_skills_increments.py` 写好结构契约与状态机行为测试（10 个失败），再实现三个 skill 增量与 claim 脚本，最后全绿——失败驱动实现，符合 T0264 的 seam 契约方法。
- **claim 状态机独立性**：`check-ticket-claims.py` 将状态写入 `tickets/claims.jsonl`（每行一个事件，可重放），`--tickets` 参数支持自定义路径——测试用临时目录隔离，避免污染仓库（首次测试曾误写仓库根 `tickets/`，已删除并加参数隔离）。
- **convergence 逐字一致**：convergence-map 文本必须与 task.json 的 4 条收敛值逐字一致（validate-convergence 校验），首次注册文本扩展版被判 `CONVERGENCE_TEXT_MISMATCH`，用 `--replace` 机制换为逐字版后 `valid: True`。
- **推翻 0809 决策**：`records/T0232-0809-ticket-dag-design-twice/conclusion.md` 曾将 expand-contract 列为不落地；本任务重新决策落地——理由是其逐批 CI 绿比例硬指标可证明重构安全性，已在 PRD 记录并 grill 确认。

### 已知边界（非本任务引入）

- 4 个全量测试失败均为既有状态：2 harness（AI-friendliness 契约 fixtures 涉及 round62-67 外部任务）+ 2 doctor（`test_doctor_uses_explicit_fallbacks`、`test_doctor_reports_seam_contracts_segment`，doctor 因 seam_contracts 检查 round62-67 外部 C++ 测试文件缺失返回 1）。`git stash` 隔离验证非本任务回归。
- LSP 静态告警（`arch_review`/`pdca_core` import 无法解析等）不影响运行时正确性。
- 增量 2 的 wide-refactor 是流程文档增量，未生成示例重构；逐批 CI 绿比例脚本断言尚未在仓库内落地为自动检查工具（skill 文档说明性指标）。

## 失败原因（仅 rejected/partial）

无。本任务全部 AC 通过，无 rejected/partial 项。

## 适用边界

- AGENT-BRIEF 质量约束的 grep 检查命令依赖 brief 文件在任务目录（`triager-brief.md`），尚未接入自动门禁（属 skill 指引性检查）。
- claim 状态机是轻量文件事件日志，无集中式锁；单仓库多 session 并行时依赖文件追加原子性（POSIX append），极端并发仍需进程级锁（后续候选）。
- wide-refactor 序列化适用于 blast radius 横跨全库的重构；小范围重构仍走垂直切片默认路径。

## 下一轮建议

1. 将 AGENT-BRIEF 质量约束接入自动门禁（triage 产出时运行 grep 检查，缺 brief 或含文件路径时拦截）。
2. 为 `check-ticket-claims.py` 增加进程级文件锁，消除极端并发下的竞态窗口。
3. 把 wide-refactor 逐批 CI 绿做成可运行脚本（记录每批提交 → 校验每批测试通过 → 输出绿比例），沉淀到 scripts/。
4. T0263（identity 观察）继续挂起等待观察窗，观察期满后出 effectiveness verdict。
