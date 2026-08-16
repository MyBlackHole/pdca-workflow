# Reactor 相位会计报告图形化改造：架构图/原理图/案例为主，文字为辅

任务 ID: T0297
场景类型: documentation
来源: T0296 结论反馈「文字内容太多，缺少架构图、原理图与案例说明」
创建: 2026-08-16

## 问题陈述

T0296（Reactor 相位会计专题）与 T0295（backupstream v65-v101 演进学习）产出的
报告以密集文字为主，缺乏架构图、原理图与数值案例，可读性差。用户反馈需图形化
改造：以图为载体、文字为辅，补充可跨项目复用的图示化表达。

## 目标

对 T0295 与 T0296 两份报告分别产出**独立图文版**，作为各自 evidence 的新版本。
遵循 code-comments 技能图示规范：Mermaid 为主 + ASCII 补充，每图 ≤20 行、
一张图一个意图、中文标签、必须带图例、用真实测试数据画案例。

## 方案

1. **T0295 图文版**（演进学习）：
   - 演进时间线 Mermaid（36 提交 → 4 条主线的 timeline/flowchart）；
   - 架构分水岭图（v70/v74/v76/v77/v80/v88/v90/v101 关键节点）；
   - 文档-代码漂移对照表（保留表格形式，辅以简单示意）；
   - 每条演进主线配 ASCII 或 Mermaid 流程图。
2. **T0296 图文版**（相位会计）：
   - 链路架构总览图（Mermaid flowchart：producer→记录→窗口→归因→诊断）；
   - 守恒分解原理图（Mermaid：callback+phase+residual==wait 可视化）；
   - 会计域不相交时序图（Mermaid sequenceDiagram：dispatch 前后埋点 vs callback）；
   - 真实数据案例：用集成测试 b-20/b-21/b-22 三案例画守恒分解条形图 + 逐步演算，
     每个诊断 finding 配数值案例。
3. 文字从"主叙事"压缩为"图的必要补充"：图例、关键结论、边界说明。

## 验收标准

- [ ] AC-1: T0295 图文版产出，含演进时间线 Mermaid 图 + 分水岭图，36 提交信息不丢失
- [ ] AC-2: T0296 图文版产出，含链路架构图 + 守恒原理图 + 会计域不相交图
- [ ] AC-3: 每个诊断 finding（internal-phase-busy/residual-delay/history-truncated）配真实测试数据的数值案例与逐步演算
- [ ] AC-4: 遵循 code-comments 图示规范：每图≤20行、一张图一个意图、中文标签、带图例
- [ ] AC-5: 两份图文版分别登记为 T0295、T0296 evidence 新版本（含 source_ids 关联）
- [ ] AC-6: 文字压缩为图的补充（不重复图已表达的信息），保留关键结论与边界说明

## 实现/测试决策

- documentation 场景无代码变更、无测试产物。
- Mermaid 语法需可用性自查（flowchart/sequenceDiagram/stateDiagram 缩进正确）。
- 事实核验以 T0295/T0296 已登记 evidence 为输入源。

## 范围外

- 不修改 backupstream 任何源码。
- 不改变 T0295/T0296 原始报告的结论与事实。
- 不改造其他历史报告。

## 备注

- 输入源：T0296 evidence `reactor-phase-accounting-report-v3`、
  T0295 evidence `git-history-learning-v3`（均已在 records/ 登记）。
- 图示规范参考 skill code-comments（已加载）。
- 产出两份独立图文版 markdown，分别登记到 T0295、T0296 records 的 evidence。