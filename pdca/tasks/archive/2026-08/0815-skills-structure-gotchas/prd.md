# skill 结构契约检查器 + Gotchas 段机制

## 问题陈述

- **现状**: 本仓库已系统性吸收 mattpocock/skills 机制（T0262 吸收、T0264 HTML 审查、T0265 三增量、T0266 三增量）。第三轮网络调研（Anthropic 官方 best practices、Anthropic 内部经验、pedronauck/skills writing-skills、claude-skills-collection、agentskills.io 生态）确认仍有 2 个**可证明**机制缺失：
  1. **无 skill 结构规范检查器**——本仓库 40 个 skill 的 frontmatter（name/description）、行数、引用深度、无 XML/Windows 路径等结构契约**没有任何脚本断言**。现有 `audit-skill-content.py` 只管流程资产契约（document/fixture 存在性），`generate-skills-index.py` 只管索引一致性，均不校验 skill 本身的结构规范。Anthropic 官方 checklist 与 pedronauck `validate-metadata.py`（agentskills.io 规范）提供现成契约可脚本化。
  2. **0/40 skill 含 Gotchas 段**——Anthropic 内部经验明确"Gotchas 是 skill 里最高信号的内容"（从真实失败点积累）。本仓库 skills 均无失败模式记录段，历史任务的真实失败点（convergence 逐字一致、git merge 返回码 1、SKILLS-INDEX 过期、register-evidence --file 唯一等）散落在归档记录中未被 skill 捕获。
- **目标**: 落地两个增量，每个配**可证明**硬指标（全量 40 skills 结构契约断言 / gotchas 段存在性断言 + 真实失败点补写）。
- **差距**: 见各增量小节。

## 解决方案

### 增量 1：skill 结构契约检查器

新增 `scripts/check-skill-structure.py`，对 `skills/*/SKILL.md` 全量执行结构契约检查（融合 Anthropic checklist + pedronauck/agentskills.io 规范）：

- **name 契约**: 长度 1–64；仅小写字母/数字/单连字符（`^[a-z0-9]+(-[a-z0-9]+)*$`）；无 XML 标记；无保留词/命令词。
- **description 契约**: 长度 1–1024；无 XML；无第一/二人称词（`i/me/my/we/our/you/your`，第三人称命令式）；含触发词（面向模型 invocation：`当`/`when`/`use`/`使用` 类触发语）。
- **体积契约**: `SKILL.md` ≤ 500 行（Anthropic 建议，渐进披露压力测试）；无 Windows 路径（`\` 反斜杠引用）。
- **引用深度契约**: 链接/上下文指针只指向 1 层（skill 自身目录内），禁止跨目录深引用。
- **Gotchas 契约**: 见增量 2。
- **完成准则契约**: 流程类 skill 的步骤以显式可检查完成准则结束（防 premature completion，pedronauck completion criterion 脚本化子集）。

**硬指标**：
- **结构级（grep/脚本可断言）**：全量 40 skills 通过全部契约，违规列表为空；`check-skill-structure.py --exit-code` 返回非 0 当存在违规。
- **行为级**：构造违规 fixture（坏 name/超长 description/超长文件）→ 检查器逐项报告并拒绝（单元测试断言）。

### 增量 2：Gotchas 段机制

- **契约**: `check-skill-structure.py` 断言每个 skill 含 `## Gotchas`（或 `## 已知坑`）段——Anthropic 判定最高信号内容，从失败点积累。
- **补写**: 为 8–10 个核心 skill 补真实 Gotchas 段，从本仓库历史任务真实失败点提取：
  - `triage-work`/`register-evidence`：convergence 文本须与 task.json 逐字一致（CONVERGENCE_TEXT_MISMATCH）；`--file` 须唯一文件名。
  - `resolving-merge-conflicts`：`git merge` 冲突返回码 1 是正常状态需 `git_allow_failure`。
  - `write-conclusion`/`write-journal`/`advance-phase`：transition 校验点（check_confirmation 须带 response 字段、阶段门禁不可绕过）。
  - `generate-skills-index` 相关：改 skill 后 `SKILLS-INDEX.md` 会过期，须重新生成。
- **写回纪律**: Gotchas 必须来自真实失败点（引用记录/任务 id），不写臆测；一条 gotcha = 一个失败点 + 防御动作。

**硬指标**：
- **结构级（grep 断言）**：目标 8–10 skill 各含非空 `## Gotchas` 段；全量 40 skills 经检查器验证无缺段。
- **真实性**: 每条 gotcha 含来源（任务 id / 记录路径），脚本抽检引用存在。

## 测试决策

- 被测模块：`scripts/check-skill-structure.py`、`skills/*/SKILL.md`（全量）。
- 好测试：检查器单元测试（违规 fixture 逐项报告）、全量 40 skills 契约断言（不测内容有效性，只测结构契约）、Gotchas 段存在性 + 来源引用抽检。
- 现有先例：`tests/test_skills_increments.py`（T0265 结构契约 grep 断言）、`test_generated_index_is_current`（全量断言）。
- 明确不做：usage measurement hook（Claude Code PreToolUse 专属，opencode 无对应机制，不可证明）；description 语义质量自动评判（人工判断）。

### 声明的测试接缝

- seam: tests/test_skill_structure.py -> scripts/check-skill-structure.py
- seam: tests/test_skill_structure.py -> skills/*/SKILL.md
- seam: tests/test_gotchas_contract.py -> skills/*/SKILL.md

## 用户故事

1. 作为 skill 维护者，我希望结构契约检查器全量校验 40 skills，以便新增/修改 skill 时机器可断言质量。
2. 作为 skill 维护者，我希望每个 skill 必须记录 Gotchas 失败模式，以便最高信号的经验不再散落。
3. 作为管理员，我希望结构契约与 Gotchas 均配可证明硬指标，以便证明其价值（全量断言 / 违规 fixture / 来源抽检）。

## 实现决策

- 语言：Python 3，单文件脚本，复用 `scripts/pdca_core.py` 或独立（T0266 先例为独立脚本）。
- 集成：`check-skill-structure.py --exit-code` 接入验证门禁；SKILLS-INDEX 重新生成。
- 范围外：usage measurement hook、description 语义自动评判、skill 内容重写（仅补 Gotchas 段）。

## 备注

- 第三轮调研来源：platform.claude.com best practices、Anthropic "Lessons from building Claude Code"、pedronauck/skills writing-skills（含 validate-metadata.py）、lionelsimai/claude-skills-collection、agentskills.io 生态。
- mattpocock 剩余弱候选（codebase-design 词汇表、prototype LOGIC.md、domain-modeling ADR 三条件、handoff argument-hint）已评估不建议单独立项，不纳入本轮。
- 口径修正：`skills/` 下正式 SKILL.md 为 **39 个**（`skills/drafts/` 为草稿区含 2 个未激活草稿，不参与检查器扫描；检查器按 `skills/*/SKILL.md` 存在性扫描）。正文 AC 中"40"均按"39 个正式 SKILL.md"执行。

## 验收标准

- [ ] AC-1: `scripts/check-skill-structure.py` 存在且可运行，对全部 `skills/*/SKILL.md` 执行 name/description/体积/引用深度/完成准则契约检查。
- [ ] AC-2: 检查器对违规 fixture（坏 name、超长 description、超长文件、XML、Windows 路径）逐项报告并返回非 0 退出码。
- [ ] AC-3: 全量 40 skills 通过全部结构契约（含 gotchas 段契约），违规列表为空（自动化断言）。
- [ ] AC-4: 全量 40 skills 各含非空 Gotchas 段（`## 已知坑` 或 `## Gotchas` 双语段名，检查器都认；桥接 skill 允许最短）。
- [ ] AC-5: 核心 9 个 skill（triage-work/register-evidence/resolving-merge-conflicts/write-conclusion/advance-phase/write-journal/design-it-twice/to-tickets/wayfinding-work）的 Gotchas 段从历史任务真实失败点提取。
- [ ] AC-6: 核心 9 个 skill 的 Gotchas 段含来源引用（任务 id/记录路径），脚本抽检引用存在。
- [ ] AC-7: 新增测试通过（检查器单元 + 全量断言 + Gotchas 契约），既有 4 失败保持非回归。
