---
schema: pdca.asset/v1
id: T0264-0815-html-architecture-review
phase: check
source_ids: [test-hotspots, test-html, arch-report, test-metrics, skill-rewrite, test-suite, arch-report-live, arch-report-as-evidence, test-task-identity, convergence-map-v3]
---

## 上下文

T0263 评估了 mattpocock/skills 与本仓库 40 个 skills 的差距，结论是 HTML 可视化报告、git 热点定位与可证明审查指标是真正差距。本任务（T0264）将 `improve-codebase-architecture` 的纯 Markdown 静态报告升级为：热点优先扫描（近 30 天 git log 频次）→ 自包含 HTML 报告（候选卡片 + before/after 可视化 + Metrics 区）→ 结构化指标登记（evidence）→ 设计闭环（grilling + design-it-twice）。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：git log 文件频次能定位高变更热点 | **supported**：`arch_review.hotspots` 在真实仓库返回 15 个热点，`scripts/pdca_core.py`、`flows/flow-plan/SKILL.md` 等高频变更文件被正确识别；无 git 历史时回退 `[]`（测试覆盖）。 |
| H2：自包含 HTML 报告可承载候选卡片与可视化 | **supported**：`render_html` 产出含 candidate-card、mermaid、Metrics、Top recommendation 的 HTML；真实运行 13774 字节，`#metrics` 数据块可被 `json.loads` 解析。 |
| H3：审查结果可量化为可证明指标序列 | **supported**：`#metrics` 报告 candidates/strong/worth/speculative/top；`arch-report` kind 可经 `register-evidence` 登记，形成跨轮次可比证据。 |
| H4：skill 升级后仍可指导完整闭环 | **supported**：`improve-codebase-architecture/SKILL.md` 重写为热点定位→HTML 生成→指标登记→设计闭环五步流程。 |
| H5：真实运行一次能产出非空报告 | **supported**：AC-8 在真实仓库运行产出 10 个候选（超长 scripts 模块自动采集）、15 个热点、指标区非空。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 hotspots 基于近 N 天 git log 频次 | test-hotspots（临时 git 仓库 fixture、无 git 回退、limit 边界） | Passed |
| AC-2 render_html 产出候选卡片 + before/after + Metrics 区 | test-html（必选 section 断言） | Passed |
| AC-3 报告写入任务目录非 /tmp，绝对路径打印 | arch-report（architecture-report.html 在任务目录） | Passed |
| AC-4 结构化指标区可机器解析 | test-metrics（`#metrics` 数据块 `json.loads`） | Passed |
| AC-5 skill 描述完整五步流程 | skill-rewrite（SKILL.md 3802 字节） | Passed |
| AC-6 审查结果可登记为 evidence（kind=arch-report） | arch-report-as-evidence（arch-report kind 成功登记） | Passed |
| AC-7 既有四维静态能力不退化 | test-suite（190 passed / 2 既有失败 / 3 deselected）+ test-task-identity | Passed |
| AC-8 真实运行一次，报告产出且指标区非空 | arch-report-live（10 candidates、15 hotspots、metrics 可解析） | Passed |

### 关键实现决策

- **collect_candidates**：按文件坏味（scripts/ 下 >200 行）自动生成深化候选，作为非空数据源；真实仓库命中 10 个超长模块。
- **Metrics 机器可解析**：`render_html` 在 `#metrics` 元素写 `data-metrics` JSON 数据块，测试用 `re.search` + `json.loads` 断言结构契约（不断言 Tailwind/Mermaid 渲染细节）。
- **ADR-0025**：记录 HTML 可视化 + 热点优先 + 指标可证明 + 设计闭环的决策与备选方案（拒绝 /tmp、拒绝 Markdown 双份、拒绝硬门禁、拒绝本地化 CDN）。
- **创建入口收敛修复**：发现 `task_identity.py` 创建任务时 `meta.convergence` 硬编码默认值 `"task identity is unique and immutable"`（继承自 T0262 语境），T0263/T0264 均受影响；新增 `--convergence` 参数（`|` 分隔）修复，T0264 收敛值已按 PRD 目标更新，T0263 将由后续 Plan 阶段修正。此为真实缺陷修复，已登记 test-task-identity 证据。

### 已知边界（非本任务引入）

- 2 个 harness 既有失败（`test_all_deterministic_fixtures_pass`、`test_public_harness_runs_real_lifecycle_success_and_transition_failures`）：AI-friendliness 契约 fixtures 涉及 round62-67 外部任务，`git stash` 隔离验证为既有状态，非本任务回归。
- LSP 静态告警（`arch_review` import 无法解析、`match.group` 潜在 None）不影响运行时正确性。
- CDN 依赖 Tailwind/Mermaid，离线时 HTML 退化纯文本仍可读（结构契约仍满足）。

## 失败原因（仅 rejected/partial）

无。本任务全部 AC 通过，无 rejected/partial 项。

## 适用边界

- 热点扫描依赖 git 历史；非 git 仓库热点为空，靠 collect_candidates 兜底非空候选。
- `collect_candidates` 目前只扫描 `scripts/` 下的超长 Python 文件，是候选的自动化来源之一；四维静态分析（flow coverage / skill consistency / knowledge-mapping / file smells）作为人工候选输入保留在 skill 中，未全部脚本化。
- Metrics 目前记录审查当次的结构分布，尚未建立跨轮次趋势聚合（后续候选）。

## 下一轮建议

1. 将 Metrics 跨轮次序列沉淀为 `knowledge/` 中的审查历史记录，形成趋势可比（指标序列的二次利用）。
2. 评估把四维静态分析的剩余维度脚本化进 `arch_review.py`，减少 skill 中的人工步骤。
3. T0263（identity 观察）继续推进 Plan：其 task.json 的 `meta.convergence` 需用 `--convergence` 参数按观察目标修正。
4. 考虑让 `arch_review` CLI 支持 `--no-cdn` 离线模式（内联 Tailwind 极小子集），降低对 CDN 的依赖。
