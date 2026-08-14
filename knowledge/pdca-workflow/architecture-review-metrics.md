---
title: 架构审查的可证明指标与 HTML 可视化报告
status: accepted
source: T0264
---

# 架构审查的可证明指标与 HTML 可视化报告

## 背景

`improve-codebase-architecture` 技能原产出纯 Markdown 静态报告，无可视化、无扫描范围策略、无结构化指标，审查结论无法跨轮次量化对比。T0264 引入热点优先扫描与结构化指标机制。

## 核心机制

1. **热点定位**：`scripts/arch_review.py::hotspots(root, days, limit)` 按近 N 天 git log 文件变更频次聚合，返回高变更路径；非 git 仓库返回 `[]`，调用方回退全量扫描。
2. **HTML 报告**：`render_html` 生成自包含 HTML（Tailwind + Mermaid CDN），每个候选一张卡片（files/problem/solution/benefits/before-after 图/recommendation badge），末尾 Top recommendation。写入任务目录 `architecture-report.html`（可提交、可作 evidence）。
3. **结构化指标区**：`#metrics` 元素带 `data-metrics` JSON 数据块（candidates/strong/worth/speculative/top），可被 `re.search` + `json.loads` 机器解析。
4. **候选数据源**：`collect_candidates(root)` 按文件坏味（scripts/ 下 >200 行）自动生成深化候选，作为非空数据源。
5. **指标登记**：审查结果经 `register-evidence --kind arch-report` 登记，形成跨轮次可比证据序列。

## 使用方式

```bash
python3 scripts/arch_review.py --root "$PWD" \
  --out pdca/tasks/<slug>/architecture-report.html \
  --days 30 --title "Architecture Review"
```

真实仓库示例输出：15 个热点 + 10 个候选（超长 scripts 模块自动采集）+ 可解析 Metrics（candidates:10, worth:10, top:smell-arch_review）。

## 经验教训

- **CDN 依赖**：Tailwind/Mermaid 走 CDN，离线时 HTML 退化为纯文本仍满足结构契约（测试不断言渲染细节）。
- **convergence 创建缺陷**：`task_identity.py` 原硬编码 `meta.convergence` 默认值 `"task identity is unique and immutable"`（继承自 T0262 语境），导致新建任务收敛值与目标不符。已新增 `--convergence "项1|项2|..."` 参数修复；创建任务必须显式传入收敛目标，否则默认沿用 identity 不变量。
- **测试断言结构契约而非实现**：热点用临时 git 仓库 fixture；HTML 只断言必选 section、字段齐全、Metrics 可解析，不断言 CDN 渲染细节。

## 关联

- `docs/adr/ADR-0025-html-architecture-review.md`
- `skills/improve-codebase-architecture/SKILL.md`
- `scripts/arch_review.py`
- `tests/test_arch_review_hotspots.py`、`tests/test_arch_review_html.py`
