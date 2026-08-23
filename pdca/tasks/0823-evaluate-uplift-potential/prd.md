# 评估 mattpocock/skills 机制对本项目的提升潜力 — PRD

## 问题陈述

T0370 报告提出了 9 条可迁移原则（P1-P9）与若干落地建议，但存在两个未验证假设：
1. 建议基于对方仓库视角提出，**未经本项目现状核实**（初查发现 code-review 的 repo-overrides 条款已存在、writing-great-skills 已由 T0245 增补双负载理论——部分建议已过时或差距缩小）。
2. "能提升"缺乏收益/成本/风险论证与验证方式，无法直接转化为 Improvement Task。

## 目标

产出评估报告 `records/T0371-0823-evaluate-uplift-potential/report.md`：对全部候选改进项做现状核实与潜力评估，给出优先级路线图与总体判定，达到可直接立项 Improvement Task 的决策质量。

## 方案

research 场景静态评估：
- E1 核实：逐项读取本项目相关文件（flows/skills/scripts/knowledge），标注 each 候选 = already-done / partial / gap
- E2 评估：五维分析（收益/成本/风险/依赖/验证方式），验证方式参照 knowledge/ai-efficiency/ai-friendliness-review-methodology.md
- E3 综合：优先级分层（立即/短期/观察/不做）+ 总体判定

## 验收标准

- [ ] AC-1: 现状核实表覆盖 ≥9 个候选项，每项标注 already-done/partial/gap 且附本项目 file:line 证据
- [ ] AC-2: 每个 partial/gap 项完成五维评估（预期收益/实施成本/风险/依赖/验证方式）
- [ ] AC-3: 路线图按 立即/短期/观察/不做 四层排序，每项附理由
- [ ] AC-4: 给出明确总体判定（能/部分能/不能提升）及支撑依据链
- [ ] AC-5: 报告登记 evidence，convergence map 验证 valid:true

## 范围外

- 不实际修改任何 flows/skills/scripts 文件（实施属后续 Improvement Task）
- 不运行 AI 友好评测实验（仅设计验证方式，执行留给实施任务）

## 备注

权威输入：records/T0370-0823-skills-ai-enhancement/report.md §6；knowledge/ai-efficiency/ 既有资产（防重复建设）；本项目 flows/skills/scripts 现状。
