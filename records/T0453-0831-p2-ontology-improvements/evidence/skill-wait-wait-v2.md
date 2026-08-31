---
schema: pdca.asset/v1
id: ontology:domain/skill-wait-wait
name: wait-wait
summary: 一句话纠偏——当消息未传达时触发。
description: 当 agent 的输出没有命中预期时，触发重新 pitch 机制——用共享语言重新表述需求。来源 mattpocock/skills wait-what。
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
---

# Wait-What — 一句话纠偏

当消息未传达时，触发重新 pitch 机制。

## 核心做法

- **一句话纠偏**：极短（3 行），避免冗长纠偏技能本身成为新的冗余
- **复用 CLAUDE.md 中已有的 leading words**
- **命名即机制**：用听众的状态名（wait-what）而非输出描述（tldr/no-fluff）
- **修复一条消息，不预防下一条**

## 适用边界

- 适用于 agent 输出未命中预期时的快速纠偏
- 共享语言构建靠 /grill-with-docs，一句话纠偏靠 wait-what

## 来源

- mattpocock/skills `skills/productivity/wait-what/SKILL.md`
- `records/T0450-0831-ontology-closed-loop-review/report.md`