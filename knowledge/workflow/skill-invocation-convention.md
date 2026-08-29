---
schema: pdca.asset/v1
id: knowledge:workflow.skill-invocation-convention
layer: knowledge
summary: "invocation: manual 标记区分用户调用和模型自动调用两类技能"
tags: [skill, invocation, convention]
scenarios: [default]
phases: [plan, do, check, act]
applies_when: [设计或修改技能调用策略]
excludes_when: []
source_ids: []
confidence: high
status: active
---

# Skill 调用约定：invocation: manual

## 概念
SKILL.md 的 YAML 前置元数据中的 `invocation: manual` 字段标记该技能**仅限用户显式请求时作为入口加载**。它可以委托 automatic worker，但 flow 和 automatic skill 不得直接调用它。

## 设计意图
区分两类技能：
1. **用户调用（交互式）** — 需要用户参与对话，如 `grill`（追问）、`domain-modeling`（术语确认）
2. **模型调用（自动化）** — AI 可在流程步骤中自主加载，如 `code-review`、`secure-coding`

## 使用规则
- 交互式入口在 frontmatter 中添加 `invocation: manual`，实际工作抽到 automatic worker
- 自动化技能不添加此字段
- flow 和 automatic skill 只能引用 automatic worker；manual 入口之间也不互相调用
- alias 与调用边由 `pdca/skill-invocation-contract.json` 声明，并由 public resolver 校验

## 适用场景
任何使用 SKILL.md 作为 AI 工作流定义的项目。
