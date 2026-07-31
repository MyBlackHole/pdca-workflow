---
schema: pdca.asset/v1
id: T0100-0727-p0-trio
layer: experience
summary: 从 mattpocock/skills 借鉴 P0 三件套并接入流程
tags: [skills, architecture, tickets, merge-conflicts]
---

# 结论: T0100 — P0 三件套

## 产出

| 技能 | 类型 | 作用 |
|------|------|------|
| improve-codebase-architecture | model-invoked | 架构嗅探 + Markdown 报告（missing/warning/info） |
| to-tickets | model-invoked | PRD→子 task.json + ID 单调递增 |
| resolving-merge-conflicts | model-invoked | 逐块分析 + 混合策略 + 验证 |

## 流程集成
- flow-plan 步骤 4：to-tickets 可选引用
- flow-do development 路径：架构检查可选（步骤 5）
- flow-do review 路径：架构检查可选（步骤 3）

## 验收
- 3 个技能全部通过 PRD 验收标准
- 流程引用已注入
