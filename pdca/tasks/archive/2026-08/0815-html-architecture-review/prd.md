# 跟进：HTML 可视化架构审查报告 + 可证明审查指标

## 问题陈述

- **现状**: `skills/improve-codebase-architecture/SKILL.md` 产出纯 Markdown 报告（`architecture-report.md`），仅做 flow 覆盖、skill 一致性、知识-流程映射、文件坏味四维静态扫描。无可视化（Mermaid before/after 图）、无扫描范围策略（全量扫而非按变更热点聚焦）、无结构化指标，审查结论无法跨轮次量化对比。
- **目标**: 架构审查产出自包含 HTML 报告（候选卡片 + before/after 可视化 + 推荐强度 badge），按近 30 天 git 变更热点聚焦扫描范围，报告内置可证明指标（候选数/采纳数/测试 seam 改善数），审查结果可登记 evidence 形成可比数据序列。
- **差距**: 缺 HTML 报告生成、缺 git 热点定位、缺结构化可证明指标、缺"审查候选→grill→设计闭环"衔接。

## 解决方案

升级 `skills/improve-codebase-architecture/SKILL.md`：
1. **热点定位**：扫描前先走 `git log`（近 30 天）找高变更区域，YAGNI——最近频繁变更的模块优先深挖；无热点时再全量扫。
2. **HTML 报告**：生成自包含 HTML（Tailwind 样式 + Mermaid before/after 图），每个候选一张卡片（files/problem/solution/benefits/before-after/recommendation badge），结尾 Top recommendation。写入任务目录 `architecture-report.html`（可提交、可作 evidence），非 `/tmp`。
3. **结构化指标区**：报告内置 `## Metrics` 区，记录候选数、Strong/Worth/Speculative 分布、Top 推荐；每次审查结果经 `register-evidence` 登记，形成跨轮次可比序列。
4. **设计闭环**：用户选定候选后接 `grilling` + `design-it-twice` 走完设计树，命名新模块时更新 `CONTEXT.md`。
5. 保留现有四维静态分析能力作为基线，HTML 报告兼容引用。

## Seam 分析

### 测试接缝

- 热点定位在 `scripts/` 内部函数边界测试：给定 git 历史，返回高变更路径集合；无 git 历史时回退全量。
- HTML 报告生成在函数边界测试：给定候选数据，产出含卡片、Mermaid 图、Metrics 区的 HTML 片段。
- 报告写入位置策略（任务目录 vs /tmp）通过调用方参数测试。

### 声明的测试接缝

- seam: tests/test_arch_review_hotspots.py -> scripts/arch_review.py
- seam: tests/test_arch_review_html.py -> scripts/arch_review.py

### 验收可测性

- 每个 AC 有 pass/fail 信号：热点返回可断言、HTML 含必选 section 可断言、指标区可解析、报告可经 register-evidence 登记。

## 用户故事

1. 作为维护者，我希望架构审查先聚焦最近高频变更的模块，以便每次审查产出最相关的深化候选，而不是平均撒网。
2. 作为审查者，我希望候选以 HTML 卡片 + before/after 图呈现，以便一眼看清模块浅化/深化差异。
3. 作为管理者，我希望每次审查的候选/采纳/测试 seam 改善可量化并沉淀为 evidence，以便证明架构改进确实提升了可测试性。

## 实现决策

- 新增 `scripts/arch_review.py`，核心接口（供技能与测试共用）：
  - `hotspots(root, *, days=30, limit=15) -> list[str]`：扫描 git log 统计文件变更频次，返回高变更相对路径；仓库无 git 历史时返回 `[]`（触发全量扫描）。
  - `render_html(candidates, *, metrics, title) -> str`：生成自包含 HTML 字符串（Tailwind CDN + Mermaid CDN），含候选卡片、before/after 图、Metrics 区。
  - CLI：`python3 scripts/arch_review.py --root <root> --out <task-dir>/architecture-report.html [--days 30]`，输出 HTML 并打印绝对路径。
- `skills/improve-codebase-architecture/SKILL.md` 重写：
  - 扫描范围步骤改为"先 `scripts/arch_review.py --hotspots`，有热点则以其为优先，否则全量"。
  - 输出改为"调用 `scripts/arch_review.py` 生成 HTML 到任务目录，打开给用户"。
  - 增加 Metrics 登记步骤：`register-evidence.py --kind arch-report --criterion <AC>`。
  - 增加设计闭环步骤：候选选定后 `grilling` + `design-it-twice`，新模块名更新 `CONTEXT.md`。
- 保留原四维分析（flow coverage/skill consistency/knowledge-mapping/file smells）作为候选输入。
- 架构决策记入 `docs/adr/ADR-0025-html-architecture-review.md`。

## 测试决策

- 被测模块：`scripts/arch_review.py`（热点定位、HTML 渲染、写入策略）。
- 好测试：热点用临时 git 仓库 fixture 断言返回频次排序；HTML 渲染断言必选 section 存在且候选字段齐全；指标区可解析为结构化数据。
- 现有先例：`tests/test_operations.py` 的临时 git 仓库 fixture、`tests/test_identity_diagnostics.py` 的临时隔离仓库模式。
- 不测 Tailwind/Mermaid 渲染细节（CDN 内容不断言），只测结构契约。

## 验收标准

- [ ] AC-1: `arch_review.hotspots` 基于近 N 天 git log 频次返回高变更路径；无 git 历史时回退全量语义。
- [ ] AC-2: `arch_review.render_html` 产出含候选卡片、before/after 可视化与 Metrics 区的自包含 HTML。
- [ ] AC-3: HTML 报告写入任务目录（非 /tmp），绝对路径打印，文件可提交。
- [ ] AC-4: 报告含结构化指标区（候选数、Strong/Worth/Speculative 分布、Top 推荐），可被机器解析。
- [ ] AC-5: `improve-codebase-architecture/SKILL.md` 完整描述"热点扫描→HTML 生成→指标登记→设计闭环"流程。
- [ ] AC-6: 审查结果可经 `register-evidence` 登记为 evidence（kind=arch-report）。
- [ ] AC-7: 既有四维静态分析能力不退化，完整相关测试集通过。
- [ ] AC-8: 在真实 PDCA 仓库运行一次完整审查，HTML 报告产出且指标区非空。

## 范围外

- 不引入自动打开浏览器（`xdg-open`）作为硬要求（无头环境可用，打印路径即可）。
- 不把架构审查设为任务 Do→Check 强制门禁。
- 不改造其他技能（tdd/grilling/design-it-twice 仅被引用）。
- 不沉淀 Tailwind/Mermaid CDN 到本地（依赖 CDN，离线时可退化纯 HTML）。

## 备注

- 术语沿用 `skills/design-it-twice/SKILL.md` 强制词汇表（module/interface/seam/adapter/depth/leverage/locality）。
- 本任务与 T0263（identity 观察）并行但独立：T0263 聚焦 AC-8 观察数据，本任务聚焦审查能力本身。
- 开发顺序：先写失败测试（热点、HTML 结构、指标解析），再实现 `arch_review.py`，再重写 skill。
