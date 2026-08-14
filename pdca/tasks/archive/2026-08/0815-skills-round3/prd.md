# 落地 mattpocock/skills 第二轮可证明增量

## 问题陈述

- **现状**: 本仓库已系统性吸收 mattpocock/skills 大多数机制（T0264 HTML 审查 + T0265 三增量）。本轮重新评估确认仍有 3 个**行为级可证明**机制缺失或滞后：
  1. `knowledge/out-of-scope/` 是空目录，out-of-scope 知识库机制从未启用——triage 只写入 `<slug>.md`（无概念级聚合、无 Prior requests 追加、无"已实现拒绝"反污染）。
  2. `resolving-merge-conflicts` 停留在**旧版策略表**（ours/theirs/manual/defer），上游已进化 intent-based（找 primary source 理解意图、保留双方意图、绝不 --abort、跑自动化检查）。
  3. `design-it-twice` 已有依赖分类，但缺 **DEEPENING 深化测试策略**（deletion test、one/two-adapter seam 纪律、replace-don't-layer）——即"如何安全深化一组浅模块"。
- **目标**: 落地三个增量，每个配**行为级**硬指标（真实状态机 fixture / 确定性决策表），比 T0265 的文档结构契约更硬。
- **差距**: 见各增量小节。

## 解决方案

### 增量 1：out-of-scope 知识库完整化

在 `skills/triage-work/SKILL.md` 的 wontfix 分支升级为概念级聚合：

- **概念聚合**：`knowledge/out-of-scope/<concept>.md` 一个概念一个文件，`## Prior requests` 段追加历史请求（含 issue/描述/日期）；同一概念的后续拒绝**追加到已有文件**，不新建。
- **反污染**：因"已实现"而拒绝的请求**禁止**写入 out-of-scope（会污染 dedup 造成假拒绝）；关闭评论指向功能已存在位置。
- **dedup 前置检查**：triage 步骤 2 读取 out-of-scope 全部文件，按概念相似度匹配；命中则 surfacing 给用户（"类似 <file> 之前拒绝过，因为 <reason>，仍要推进？"）。
- **写入条件**：仅 enhancement（非 bug）被 wontfix 拒绝时写入；reason 必须 durable（避免"现在太忙"这类临时理由——那是 deferral 非拒绝）。

**实现**：新增 `scripts/out-of-scope-manager.py`（聚合逻辑：add/list/check），复用 claim 状态机模式。

**硬指标**：
- **行为级**：fixture 断言"同一概念第二次请求追加到已有文件、文件数不变；不同概念新建文件"。
- **行为级**：反污染——"已实现"拒绝路径不写 out-of-scope（断言）。
- **结构级**：out-of-scope 文件含 `## Prior requests` 段（grep 断言）。

### 增量 2：resolving-merge-conflicts 升级 intent-based

将 `skills/resolving-merge-conflicts/SKILL.md` 从策略表升级为 intent-based：

1. **看当前状态**：merge/rebase 进行中，列出冲突文件。
2. **找 primary source**：对每个冲突读 commit message、PR、issue，理解原始意图——为什么改、期望是什么。
3. **逐 hunk 解析**：尽量**保留双方意图**；不兼容时选符合 merge 目标的那个并记录权衡；**绝不发明新行为**；**绝不 --abort**。
4. **跑自动化检查**：typecheck → tests → format，修复 merge 破坏的。
5. **完成 merge**：stage + commit；rebase 则继续到全部 commit rebase 完成。

**硬指标**：
- **行为级**（真实 git fixture）：构造 merge 冲突 → 按 intent 解析 → 断言"解析完成不 abort、`git diff --check` 无残留标记、双方意图内容均保留"。
- **结构级**：skill 文档含 `never abort`/`primary source`/`preserve both intents`/`automated checks` 契约关键词。

### 增量 3：design-it-twice 补 DEEPENING 深化测试策略

在 `skills/design-it-twice/SKILL.md` 补"深化测试策略"章节：

- **deletion test**：想象删除模块——若复杂度消失，它是 pass-through；若复杂度散布到 N 调用点，它在挣自己的存在。
- **seam 纪律**：**一个 adapter = 假设性接缝，两个 = 真实接缝**——没有至少两个 adapter（通常生产+测试）不要引入 port，单 adapter 接缝只是间接层。
- **内部接缝 vs 外部接缝**：深模块可有内部接缝（实现私有，供自身测试），但不要因测试使用就把内部接缝暴露到接口。
- **replace, don't layer**：深化接口的测试一旦存在，浅模块的旧单测变废物——**删除**；新测试在深化接口处写；测试断言接口外的可观察结果而非内部状态；测试应挺过内部重构（行为非实现）。

**硬指标**：
- **行为级**：依赖分类（in-process/local-substitutable/remote-owned/true-external）→ 测试策略的**确定性决策表**，脚本断言 4 类依赖各映射到正确策略（路由合约模式）。
- **结构级**：design-it-twice 文档含 seam 纪律段落（grep 断言）。

## 测试决策

- 被测模块：`skills/triage-work/SKILL.md`、`skills/resolving-merge-conflicts/SKILL.md`、`skills/design-it-twice/SKILL.md`、`scripts/out-of-scope-manager.py`。
- 好测试：out-of-scope 聚合状态机（临时目录 fixture）、merge-conflicts 真实 git fixture（`git merge` 构造冲突）、DEEPENING 决策表（确定性映射）。
- 现有先例：`tests/test_skills_increments.py`（T0265 结构契约 + claim 状态机）、`run-ai-friendliness-fixtures.py`（路由合约）。
- 不测内容有效性，只测结构契约 + 行为状态机。

### 声明的测试接缝

- seam: tests/test_out_of_scope.py -> scripts/out-of-scope-manager.py
- seam: tests/test_out_of_scope.py -> skills/triage-work/SKILL.md
- seam: tests/test_merge_conflicts_intent.py -> skills/resolving-merge-conflicts/SKILL.md
- seam: tests/test_deepening_policy.py -> skills/design-it-twice/SKILL.md

## 用户故事

1. 作为 triage 执行者，我希望 wontfix 按概念聚合到 out-of-scope 知识库，以便 dedup 时能 surfacing 历史拒绝理由。
2. 作为 triage 执行者，我希望"已实现"的拒绝不写入 out-of-scope，以便不污染 dedup 造成假拒绝。
3. 作为 merge 冲突解析者，我希望按意图解析而非策略表，以便保留双方真实意图且绝不中途放弃。
4. 作为接口设计者，我希望 design-it-twice 能指导深化浅模块集群，以便安全地减少模块数量。
5. 作为管理员，我希望每个增量有行为级硬指标，以便证明其价值（真实 git fixture / 确定性决策表）。

## 实现决策

- 增量 1 新增 `scripts/out-of-scope-manager.py` + 测试；增量 2 重写 skill + 测试；增量 3 补 skill 章节 + 测试。
- 三个增量均为 skill 文档 + 脚本 + 测试，无运行时代码影响。
- 历史已有 out-of-scope 空目录 `knowledge/out-of-scope/.gitkeep`，机制启用后真实拒绝会填充。

## 验收标准

- [ ] AC-1: `out-of-scope-manager.py` 实现 add/list/check，同概念追加已有文件（文件数不变）、不同概念新建文件。
- [ ] AC-2: "已实现"拒绝路径不写 out-of-scope（反污染断言）。
- [ ] AC-3: `triage-work/SKILL.md` wontfix 分支描述概念聚合 + Prior requests 追加 + dedup 前置检查 + 仅 enhancement 写入。
- [ ] AC-4: `resolving-merge-conflicts/SKILL.md` 升级 intent-based（primary source/preserve both intents/never abort/automated checks）。
- [ ] AC-5: merge-conflicts 真实 git fixture：解析完成不 abort、`git diff --check` 无残留标记、双方意图保留。
- [ ] AC-6: `design-it-twice/SKILL.md` 补 DEEPENING 深化测试策略（deletion test、seam 纪律、replace-don't-layer）。
- [ ] AC-7: DEEPENING 依赖分类→测试策略确定性决策表脚本断言通过。
- [ ] AC-8: 新增测试全绿，全量测试无回归（4 既有失败非本轮引入）。

## 范围外

- 不引入 .out-of-scope 目录结构变更（沿用 `knowledge/out-of-scope/`）。
- 不落地弱候选（ADR 三条件收紧、prototype lift、handoff argument-hint、grill-me、PHASE-BOUNDARIES、git-guardrails）。
- 不实现 merge-conflicts 的 UI 工具或 IDE 集成，仅 skill + fixture。
- 不修改 flow-plan / flow-do 主流程门禁。

## 备注

- 本轮增量的可证明性比 T0265 更硬：out-of-scope 聚合与 merge-conflicts 解析是**行为级**（真实状态机 fixture），DEEPENING 是**确定性决策表**。
- 方法论延续 T0264/T0265：失败驱动实现（先写红测试再实现）、行为级指标优先。
- 术语沿用既有 skill 词汇。
