# Triage Brief — 审查+增强 writing-great-skills（writing-for-agents 4 杠杆）

## 分类

- category: enhancement
- scenario_type: development（修改技能资产 skills/writing-great-skills/SKILL.md）
- 去重：本地 skills/writing-great-skills/SKILL.md 存在（60 行），无先例任务。
  mattpocock writing-for-agents 全文已拉取对比。

## 审查结论（P0 已核实）

本地 writing-great-skills 已覆盖：信息层级、极简原则、否定反模式、过早完成、
去沉积、user-invoked/model-invoked、完成标准。**缺失 4 个杠杆**：

| 杠杆 | mattpocock 内容 | 本地现状 |
|------|----------------|---------|
| L1 锚定词（leading words） | 用预训练已有词锚定行为（_tight_ 紧凑循环、_red_ 红灯），重复用 token 不用句子 | 无 |
| L2 指针措辞（context pointer） | 指针措辞（非目标）决定触发可靠性；弱措辞=方差 bug；一分支一触发词；前置首词 | 只说"上下文指针"，未讲措辞作用 |
| L3 双负载（two loads） | context load（常载 token）+ cognitive load（人工索引）；渐进披露是保护层级，非纯 token 优化 | 无成本模型 |
| L4 no-op 模型相对测试 | "是否改变默认行为"是模型相对的，分歧靠运行文档解决，非辩论；负词太弱是 no-op，换更强词 | 有"无操作不写"但无模型相对判定 |

## 信息缺口

- 无。writing-for-agents 原文已完整拉取，4 杠杆内容核实。

## 推荐下一步

- Plan：设计 4 杠杆落地为 writing-great-skills 章节增补 + 契约测试守护
  （机器可读断言 L1-L4 落地点）
- 内容预算：SKILL.md 60 行约 2.3KB → 增补后约 3.5-4KB，需按 ADR-0007
  豁免流程记录
