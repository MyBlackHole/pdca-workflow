# 落地 mattpocock/skills 三个可证明增量

## 问题陈述

- **现状**: 本仓库 skills 已系统性吸收 mattpocock/skills 大多数机制（grilling frontier 批量问、wayfinder HITL/AFK、HTML 架构审查报告 + 可证明指标等）。重新评估后确认仍有 3 个**可被硬指标证明价值**的机制缺失：
  1. `triage-work` 的 `triager-brief.md` 只有一句话定义，无结构化模板与质量约束 → brief 质量不可检查。
  2. `to-tickets` 只有垂直切片 + 依赖边，无 wide-refactor 分支 → 全局改名/改类型时单提交打穿全部调用点，无法保证逐批 CI 绿。
  3. `wayfinding-work` 选票后直接执行，无 claim（认领）机制 → 并发 session 会同时处理同一张票。
- **目标**: 落地三个增量，每个配可证明的硬指标与测试。
- **差距**: 见各增量小节。

## 解决方案

### 增量 1：triage-work 补 AGENT-BRIEF 结构化模板与可检查质量约束

在 `skills/triage-work/SKILL.md` 的 `## 5. Output` 增加 `triager-brief.md` 结构化模板：

```markdown
# Triage Brief — <slug>

- **category**: <bug|enhancement>
- **scenario_type**: <development|bugfix|research|documentation|design|review>
- **summary**: <请求一句话>
- **current behavior**: <现状行为>
- **desired behavior**: <期望行为>
- **key interfaces**: <相关模块/接口，不写文件路径>
- **acceptance criteria**: <每条独立可验证，格式"运行 X 得到 Y">
- **out of scope**: <明确排除项>
- **information gaps**: <信息缺口>
- **dedup results**: <查重结果>
- **recommended next steps**: <建议>
```

质量约束（可机器检查）：
- **AC 可测性**：每条 AC 含"运行 X 得到 Y"可验证信号，不写文件路径/行号。
- **durability over precision**：不写 `:line`、具体文件路径或实现结构。
- **覆盖**：ready-to-plan 任务必须有 `triager-brief.md`。

**硬指标**：
- `grep -c ':line\|<file path>' triager-brief.md == 0`（禁止项检查）
- ready-to-plan 任务的 brief 覆盖率 = 100%（可断言）
- AC 存在性：brief 含 `acceptance criteria` 段（可断言）

### 增量 2：to-tickets 补 wide-refactor 保绿序列化

在 `skills/to-tickets/SKILL.md` 的 Process 后增加 wide-refactor 分支：

当重构的 blast radius 横跨全库（全局改名/改类型/改接口签名）时，禁止单提交打穿：
1. **expand**：新旧形式并存（新增新接口/新名，保留旧形式），一个 expand 子任务。
2. **分批迁移**：按 blast radius 分批，每批一个子任务（`blocked by expand`），每批迁移后跑完整测试，保持 CI 绿（逐批绿）。
3. **contract**：无调用者后删除旧形式，一个 contract 子任务（`blocked by` 全部迁移批）。
4. 批内无法保绿时：共享集成分支 + 末尾 integrate-and-verify 票。

`dependencies` 声明这批 blocking edges（expand → 迁移批 → contract）。

**硬指标**：
- 重构期间逐批 CI 绿比例 = 100%（每批提交跑测试，可脚本断言）。
- expand 阶段旧形式仍存在的契约测试（可断言旧接口未被删除）。
- 单批迁移调用点数上限可审计。

### 增量 3：wayfinding-work 补 ticket claim 并发防冲突

在 `skills/wayfinding-work/SKILL.md` 的步骤 2 与 3 之间插入认领：

1. **claim**：选票后立即在 ticket 状态文件标记 `claimed-by: <session-id>` + `in-progress`。
2. 只有 `open + unblocked + unclaimed` 的票是可选 frontier。
3. 并发 session 读取 MAP 时跳过已认领票。
4. 完成后更新为 `resolved`，清除 claim。

在 `skills/wayfinding-chart/SKILL.md`（或 tickets 模板）加入 claim 字段说明。

**硬指标**：
- tickets 状态机脚本检测"同一票被两 session 同时标 in-progress"（冲突率）。
- claim → resolve 的单票完成时间可归因到 session。

## 测试决策

- 被测模块：`skills/triage-work/SKILL.md`、`skills/to-tickets/SKILL.md`、`skills/wayfinding-work/SKILL.md` 的文档结构。
- 好测试：用 grep/正则断言 skill 文件含新增模板段与约束关键词；对 wayfinding claim 用状态机 fixture 断言冲突检测。
- 现有先例：`tests/test_operations.py::test_generated_index_is_current`（断言 skill 文档含指定段）、`tests/test_arch_review_*.py`（文档结构断言模式）。
- 不测内容有效性，只测结构契约（模板存在、约束字段齐全、claim 状态机行为）。

### 声明的测试接缝

- seam: tests/test_skills_increments.py -> skills/triage-work/SKILL.md
- seam: tests/test_skills_increments.py -> skills/to-tickets/SKILL.md
- seam: tests/test_skills_increments.py -> skills/wayfinding-work/SKILL.md

## 用户故事

1. 作为 triage 执行者，我希望 triager-brief 有结构化模板与可检查的质量约束，以便产出可直接进入 Do 的高质量 brief。
2. 作为 wide-refactor 执行者，我希望 to-tickets 提供 expand→分批迁移→contract 序列化，以便每次提交后 CI 保持绿色。
3. 作为并发 session 的执行者，我希望 wayfinding 有 claim 机制，以便多 session 不会重复处理同一张决策票。
4. 作为管理员，我希望每个增量有可脚本断言的硬指标，以便证明其价值。

## 实现决策

- 三个增量均修改 skill 文档（markdown），增量 3 额外可能新增 `scripts/check-ticket-claims.py`（状态机冲突检测）。
- 新测试文件 `tests/test_skills_increments.py`，用正则断言文档结构契约。
- 历史任务 `0809-ticket-dag-design-twice` 曾明确"不落地 expand-contract"——本任务重新决策：expand-contract 现在有可证明的逐批 CI 绿指标，故落地（需 grill 确认）。

## 验收标准

- [ ] AC-1: `triage-work/SKILL.md` 含 AGENT-BRIEF 结构化模板（category/summary/current/desired/interfaces/AC/out-of-scope 等字段）。
- [ ] AC-2: 模板含可检查质量约束（AC 可测性、durability over precision 禁 `:line`/文件路径、ready-to-plan 必须有 brief）。
- [ ] AC-3: `to-tickets/SKILL.md` 含 wide-refactor 分支（expand→分批迁移→contract→integrate 票），并说明依赖边声明方式。
- [ ] AC-4: wide-refactor 分支含逐批 CI 绿硬指标与 expand 阶段旧形式契约测试说明。
- [ ] AC-5: `wayfinding-work/SKILL.md` 含 claim 机制（claimed-by/in-progress 字段、只有 unclaimed 票可取、并发跳过）。
- [ ] AC-6: claim 有冲突检测可证明性（状态机脚本或测试断言）。
- [ ] AC-7: 新增 `tests/test_skills_increments.py` 断言三 skill 的结构契约，测试通过。
- [ ] AC-8: 相关测试集通过（无回归），既有 skill 测试不退化。

## 范围外

- 不实现 ticket tracker 适配层（集中式 `$PDCA_HOME` 架构不需要）。
- 不落地 to-questionnaire / wait-what / wizard / teach 等已排除项。
- 不修改 `flow-plan` / `flow-do` 主流程门禁。
- 不做 writing-for-agents 的 demand/router/environment-cache 弱可证明点。

## 备注

- 三个增量的"可证明"均依赖测试断言（结构契约 + 行为状态机），与 T0264 的可证明指标方法论一脉相承。
- 增量为 skill 文档 + 测试，无运行时代码影响。
- 术语沿用现有 skill 词汇（ticket/frontier/blocking edge/ready-set 等）。
