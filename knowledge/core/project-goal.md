---
schema: pdca.asset/v1
id: knowledge:core/project-goal
layer: knowledge
summary: PDCA 项目的使命是提升 AI 处理任意事情的效率、准确性和可复用性
tags: [project-goal, pdca, knowledge, experience, skills, ai-efficiency]
scenarios: [default]
phases: [plan, do, check, act]
applies_when: [设计流程、组织知识经验、创建或复用 skill、评估新功能时]
excludes_when: []
source_ids: [experience:T0060--07-26-记录-pdca-项目主要目标与效率使命]
confidence: high
status: active
---

# 项目主要目标

## 根本目的

提高 AI 使用效率与事情处理的效率、准确性和可复用性，使 AI 能稳定处理开发、调研、分析、设计、审查、文档等任意场景。

## 核心能力

1. **PDCA 流程管理**：用 Plan、Do、Check、Act 组织问题定义、执行验证、结果判断和闭环改进。
2. **知识与经验管理**：区分可复用知识与单次任务经验，保存来源、证据、适用条件和边界。
3. **Skills 管理**：创建、维护、校验和按场景加载流程 skill 与辅助 skill。
4. **历史复用**：新任务开始时检索与当前任务最相关的历史知识、经验、证据和 skill，减少重复探索。
5. **经验生成 Skills**：从稳定、可复用的任务经验中提炼新的 skill，使系统持续积累能力。

## 能力闭环

```text
新任务
  → 检索历史知识/经验/skills
  → PDCA 执行与证据记录
  → Check 判断适用性
  → Act 归档经验
  → 将稳定经验提炼为知识或 skill
  → 服务后续任务
```

## 设计原则

- 先建立可验证的假设，再执行工作。
- 事实、证据、经验、知识和 skill 分层存放，保持来源可追溯。
- 只有经过验证且具备跨任务适用性的经验，才生成共享知识或 skill。
- AI 应优先复用已有可靠内容，再开始新的探索。
- 所有自动化都服务于效率、准确性和可复用性，不为增加流程而增加流程。
