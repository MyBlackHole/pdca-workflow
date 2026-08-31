---
schema: pdca.asset/v1
id: ontology:concept/skill-mechanics
type: concept
layer: Knowledge
status: active
summary: 技能编写机制参考——invocation 选择、router 模式、依赖表达
description: "定义技能编写的三种机制：Invocation（model-invoked vs user-invoked 的精确机制）、Splitting by invocation（有独立触发词或另一技能需调用时拆为 model-invoked）、Router skills（user-invoked 技能过多时的路由模式）。来源 mattpocock/skills writing-for-agents SKILL-MECHANICS.md。"
domain:
- ontology:domain/ai-efficiency
relations:
  specializes:
  - ontology:domain/ai-efficiency
  relates_to:
  - ontology:concept/writing-for-agents
  - ontology:concept/pointer-wording
attributes:
- name: applicability
  desc: 技能编写时选择 invocation 模式和 router 模式的适用场景
  constraint: 见正文
  testable_signal: 技能 SKILL.md 的 frontmatter 包含正确的 invocation 配置
- name: constraints
  desc: user-invoked 不可调用其他 user-invoked；model-invoked 可被 user-invoked 调用
  constraint: 遵循 invocation 层级规则
  testable_signal: 检查所有 user-invoked 技能的依赖关系无循环
- name: testable_signal
  desc: 由领域实践与测试验证 invocation 配置正确性
  constraint: 由领域实践与测试验证
  testable_signal: 检查所有 user-invoked 技能的依赖关系无循环，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空
---

# 技能机制（Skill Mechanics）

定义技能编写的三种核心机制，来源 mattpocock/skills `writing-for-agents/SKILL-MECHANICS.md`。

## 1. Invocation 选择

### model-invoked

- **标记**：省略 `disable-model-invocation`（Claude Code）/ 不设 `policy.allow_implicit_invocation: false`（Codex）
- **谁调用**：AI 自动 + 用户均可
- **规则**：可调用 model-invoked，不可调用其他 user-invoked
- **描述**：需写清触发条件（`description` 面向模型带触发条件短语）

### user-invoked

- **标记**：`disable-model-invocation: true`（Claude Code）/ `policy.allow_implicit_invocation: false`（Codex）
- **谁调用**：仅用户打字
- **规则**：可调用 model-invoked，不可调用其他 user-invoked
- **描述**：面向人类，`description` 用自然语言

### 关键约束

- **user-invoked 不可调用其他 user-invoked**（包括通过 Skill tool 按名称调用）
- **model-invoked 可被 user-invoked 调用**
- 依赖表达方式：显式 `Call the Skill tool with "name"`，而非 `/name` 风格的 hint

## 2. Splitting by invocation

当满足以下任一条件时，技能应拆分为 model-invoked：

- 有独立触发词
- 另一技能需调用它
- 步骤太长导致 AI 想跳步

## 3. Router skills

当 user-invoked 技能过多时，使用 router 技能进行路由：

- 一个 user-invoked 技能命名其他技能及何时使用
- 依赖表达方式：显式 `Call the Skill tool with "name"`
- router 本身应为 user-invoked

## 4. 完整调用层级

```
user-invoked → model-invoked → model-invoked
     ↓              ↓              ↓
  grill-me     grilling     tdd
  ask-matt     researching  code-review
  wayfinder    prototype    domain-modeling
```

## 适用边界

- 适用于所有 skill 文件的 frontmatter 设计和 invocation 配置
- 对本地 `skill-writing-great-skills.md` 和 `skill-ask-matt.md` 有直接参考价值
- 与 `ontology:concept/skill-invocation-contract` 互补：skill-mechanics 定义机制，skill-invocation-contract 定义契约

## 来源

- `records/T0450-0831-ontology-closed-loop-review/report.md`（来源 ID: T0450-0831-ontology-closed-loop-review）
- mattpocock/skills `writing-for-agents/SKILL-MECHANICS.md`