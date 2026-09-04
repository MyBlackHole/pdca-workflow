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
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-wait-wait/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/grilling-methodology
    - ontology:concept/leading-words
  testable_signal: "运行 grep -q 'Wait-What — 一句话纠偏' ontology/domain/pdca/skill-wait-wait.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


# Wait-What — 一句话纠偏

user-invoked：当 agent 的输出没有命中预期时，触发重新 pitch 机制。

## 核心做法

- **一句话纠偏**：极短（3 行），避免冗长纠偏技能本身成为新的冗余
- **复用 CLAUDE.md 中已有的 leading words**
- **命名即机制**：用听众的状态名（wait-what）而非输出描述（tldr/no-fluff）
- **修复一条消息，不预防下一条**

## 触发条件

当 agent 的输出没有命中预期时触发：
- 消息未传达
- 输出与预期不符
- 需要重新 pitch

## 纠偏策略

1. **识别偏差**：确定 agent 输出与预期的偏差
2. **复用 leading words**：用 CLAUDE.md 中已有的锚定词重新表述
3. **一句话纠偏**：用极短（3 行）重新 pitch
4. **不预防下一条**：只修复当前消息，不做预防性修改

## 适用边界

- 适用于 agent 输出未命中预期时的快速纠偏
- 共享语言构建靠 /grill-with-docs，一句话纠偏靠 wait-wait
- 与 Negative Space 互补：wait-wait 修复已发送的消息，Negative Space 预防省略的决策

## 来源

- mattpocock/skills `skills/productivity/wait-what/SKILL.md`
- `records/T0450-0831-ontology-closed-loop-review/report.md`