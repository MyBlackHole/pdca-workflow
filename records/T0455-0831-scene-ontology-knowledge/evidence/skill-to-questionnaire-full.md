---
schema: pdca.asset/v1
id: ontology:domain/skill-to-questionnaire
name: to-questionnaire
summary: Turn a decision you cannot answer alone into a Markdown questionnaire.
description: 面试发送而非主题：将无法独自回答的决策转化为 Markdown 问卷，发给能回答的人。来源 mattpocock/skills to-questionnaire。
invocation: user-invoked
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/grilling-methodology
    - ontology:concept/leading-words
    - ontology:concept/skill-mechanics
---

# To Questionnaire — PDCA 问卷

user-invoked：将无法独自回答的决策转化为 Markdown 问卷，发给能回答的人。

## 核心做法

- **面试发送，而非主题**：问卷问的是"发给谁、需要什么回传"，而非决策本身
- **异步或同步**：可单独填写，也可一起讨论
- **是 /grill-me 的逆运算**：grill-me 面试主题，to-questionnaire 面试发送对象

## 流程

1. 确定无法独自回答的决策
2. 确定能回答的人
3. 编写问卷：发给谁、需要什么回传
4. 发送问卷并等待回复

## 问卷结构

每个问卷应包含：
- **决策背景**：为什么需要这个决策
- **问题列表**：具体要问的问题
- **回传要求**：期望的回复格式和截止时间
- **相关上下文**：让回答者快速理解背景的链接或引用

## 适用边界

- 适用于需要他人输入但无法面对面讨论的决策场景
- 对本地 to-spec 流程有补充价值
- 与 grill-me 互补：grill-me 用于需要实时对话的决策，to-questionnaire 用于异步决策

## 来源

- mattpocock/skills `skills/productivity/to-questionnaire/SKILL.md`
- `records/T0450-0831-ontology-closed-loop-review/report.md`