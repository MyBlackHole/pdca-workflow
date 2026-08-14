---
schema: pdca.adr/v1
id: ADR-0025
title: HTML 可视化架构审查报告与可证明审查指标
status: Accepted
date: 2026-08-15
---

# ADR-0025: HTML 可视化架构审查报告与可证明审查指标

## 背景

`skills/improve-codebase-architecture` 原产出纯 Markdown 静态报告，无可视化、无扫描范围策略、无结构化指标，审查结论无法跨轮次量化对比。T0264 引入 HTML 可视化与可证明指标机制。

## 决策

1. **热点定位优先**：`scripts/arch_review.py::hotspots` 按近 30 天 git log 文件变更频次返回高变更路径；无 git 历史时返回空列表，调用方回退全量扫描（YAGNI——最近频繁变更的模块优先深挖）。
2. **HTML 报告写入任务目录**：`render_html` 生成自包含 HTML（Tailwind CDN + Mermaid CDN），每个候选一张卡片（files/problem/solution/benefits/before-after 图/recommendation badge），末尾 Top recommendation。写入任务目录 `architecture-report.html`（可提交、可作 evidence），非 `/tmp`。
3. **结构化指标区**：报告内置 `#metrics` 数据块（candidates/strong/worth/speculative/top），机器可解析；审查结果经 `register-evidence --kind arch-report` 登记，形成跨轮次可比序列。
4. **候选数据源**：`collect_candidates` 按文件坏味（>200 行）自动生成深化候选，作为非空数据源。
5. **设计闭环**：选定候选后接 `grilling` + `design-it-twice`，新模块名更新 `CONTEXT.md`。

## 备选方案

- **写 /tmp + 自动打开浏览器**：仓库干净但无法作 evidence，无头环境不可用 → 拒绝。
- **Markdown + HTML 双份**：冗余维护 → 拒绝，HTML 单份替代。
- **审查设为 Do→Check 硬门禁**：过重，按需调用 → 拒绝。
- **本地化 Tailwind/Mermaid**：增加维护成本，CDN 依赖可接受，离线退化纯 HTML → 接受。

## 影响

- `skills/improve-codebase-architecture` 重写：热点扫描→HTML 生成→指标登记→设计闭环。
- 新增 `scripts/arch_review.py`（hotspots/render_html/collect_candidates/CLI）。
- 审查质量可证明：候选数/采纳数/测试 seam 改善数经 evidence 沉淀。
- 保留原四维静态分析（flow coverage/skill consistency/knowledge-mapping/file smells）作为候选输入。
