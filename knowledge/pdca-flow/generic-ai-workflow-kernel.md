---
schema: pdca.asset/v1
id: knowledge:pdca-flow.generic-ai-workflow-kernel
layer: knowledge
summary: PDCA 作为任意 AI 工作场景外循环的架构原则（历史设计笔记精简版）
tags: [pdca-flow, architecture, historical]
scenarios: [default]
phases: [plan, do, check, act]
applies_when: [理解当前 PDCA 工作流的架构理念]
excludes_when: []
source_ids: []
confidence: medium
status: active
---

# 通用 AI 工作流 Kernel — 设计原则

以下原则是早期架构探索的结论，已在当前 PDCA 流程中落地：

## 已落地原则

| 原则 | 当前体现 |
|------|---------|
| PDCA 作为稳定外循环 | `flows/flow-{plan,do,check,act}/SKILL.md` |
| 领域行为由场景契约提供 | `task.json` → `meta.scenario_type` → 6 条 Do 路径 |
| Check 产物是 Evidence | `records/<id>/evidence/` + `manifest.jsonl` |
| 阶段 Decision 必须引用证据 | flow-check 的 verify-convergence 门禁 |
| Artifact 类型保持开放 | 文件、URL、报告均可作为证据 |

## 未落地（已弃用）

- **Scenario Contract serde / `pdca scenario validate`** — 当前无 Rust CLI，用 `task.json` 字段替代
- **Observation Journal** — 用 `pdca/journal/` 和 `records/` 替代
- **Planner / Executor / Validator 三层分离** — 当前由 AI agent 统一承担
- **跨进程锁 / 幂等键 / JSONL 审计日志** — 当前单 agent 串行执行，不需要

## 历史教训

- 通用调度器容易过度抽象：应先交付可用的文件级流程再考虑运行时
- 场景版本绑定到任务抽象正确：当前用 `task.json` 的 `meta.scenario_type` 实现
- 阻塞原因应输出结构化数据：当前 flow-do 通过 `clarifications.jsonl` 实现