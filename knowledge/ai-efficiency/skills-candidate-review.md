---
schema: pdca.asset/v1
id: knowledge.ai-efficiency.skills-candidate-review
summary: 技能候选系统化审查方法论——审查前先核实本地现状（对象修正）、逐候选深挖原文差距、可证明收益假设优先、产出含判定与优先级（T0242 实例：4 候选仅 1 处增强，D1-D6 深挖确认）
tags: [ai-efficiency, skills, review, mattpocock, assessment]
scenarios: [do, act]
phases: [do, check]
source_ids: [T0242-0809-skills-candidates-review, T0243-0809-diagnosing-bugs-enhance]
---

# 技能候选系统化审查（Skills Candidate Review）

## 核心做法

对"外部技能候选"（如 mattpocock/skills）做落地评估，三个已验证要点：

1. **审查前先核实本地现状**。P0 阶段先查本地是否已有等价技能，再决定评估
   对象是"引入缺失"还是"已有 vs 原文差距"。T0242 中 4 候选 3 个已存在，
   若跳过此步会误判为"待引入"。
2. **逐候选深挖原文差距**。拉取原文 SKILL.md 与本地逐条核对，不凭印象。
   产出差异表（编号 D-n：原文有/本地无、影响、价值）。
3. **可证明收益优先 + 判定三态**。每候选给出落地/不落地/增强判定 + 收益
   假设（可测试），不落地要有明确依据（已覆盖且超越）。

## 实例判定（T0242）

| 候选 | 判定 | 依据 |
|------|------|------|
| diagnosing-bugs | 增强 | 本地有 Phase 骨架，缺 6 处细节 |
| code-review 双轴 | 不落地 | 本地已实现且超越（Fowler 坏味 + 双执行器并行） |
| CI 基础设施 | 候选 | 工具链就绪但依赖平台（T0241 doctor 已兜底） |
| handoff/wayfinder | 不落地 | 本地完整且更结构化 |

## 增强落地（T0243）

diagnosing-bugs 增强已作为独立任务落地（`skills/diagnosing-bugs/SKILL.md`
55→约 100 行）：Phase 0 合并 Redact（D1）+ CONTEXT 读取（D6），Phase 2 加
无环显式停止门禁（D3）与非确定性指引（D2），Phase 3 假设改双向预测，
Phase 6 加架构移交（D5），HITL 模板 hitl-loop.template.sh（D4）。
每条差异均有契约测试机器可读断言守护（AC-7），内容预算基线豁免按
流程显式更新。判定三态 → 增强的候选应尽快独立成任务落地，避免
审查报告停留在"建议"层面。

## 深挖差异优先级（diagnosing-bugs 实例）

D1（安全 Redact）> D3（无环显式停止门禁）> D2（非确定性 bug）>
D4（HITL 兜底）> D5（post-mortem 架构移交）> D6（CONTEXT 前置 + 双向预测）。

排序原则：**安全/门禁类价值 > 能力补齐类 > 细节完善类**。

## 复用场景

- 任何外部技能/模板/工具候选的落地评估（新增、对比、增强）。
- 收割线收尾的"新候选重新审查"（T0233 conclusion 建议，T0242 验证）。

## 边界

- 审查任务只产出报告，落地需另开 Improvement Task（T0242 仅审查）。
- 外部平台依赖的候选（如 CI）判定依赖用户决策，报告需明示。
