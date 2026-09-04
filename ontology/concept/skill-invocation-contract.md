---
schema: pdca.asset/v1
id: ontology:concept/skill-invocation-contract
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-invocation-contract/1.0.0
summary: 双 harness 调用约定与 openai.yaml 元数据规范
description: "定义 Claude Code 和 Codex 双 harness 的调用模型：每个 SKILL.md 旁放 agents/openai.yaml 含 Codex UI 元数据；user-invoked 技能设 disable-model-invocation: true（Claude Code）/ policy.allow_implicit_invocation: false（Codex）；依赖通过 Call the Skill tool with \"name\" 显式调用。来源 mattpocock/skills .agents/invocation.md。"
domain:
- ontology:domain/ai-efficiency
relations:
  specializes:
  - ontology:domain/ai-efficiency
  relates_to:
  - ontology:concept/pointer-wording
  - ontology:concept/skill-mechanics
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 双 harness 环境下技能调用约定的适用场景
  constraint: 见正文
  testable_signal: 检查所有 SKILL.md 旁是否有 agents/openai.yaml，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空
- name: constraints
  desc: 每个 SKILL.md 必须配 agents/openai.yaml；user-invoked 必须设 disable-model-invocation
  constraint: 遵循双 harness 调用约定
  testable_signal: 运行 python3 scripts/check-skill-structure.py 检查所有 SKILL.md 旁是否含 agents/openai.yaml，缺失时退出非0
- name: testable_signal
  desc: 双 harness 调用约定按 frontmatter 与 agents/openai.yaml 可机检判定
  constraint: 每个 SKILL.md 须配 agents/openai.yaml 且 user-invoked 标记合法，缺失或非法即失败
  testable_signal: 运行 python3 scripts/check-skill-structure.py 检查 SKILL.md 旁 agents/openai.yaml 存在性与 user-invoked 标记，且 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空，任一检查非0即失败
---

# 技能调用契约（Skill Invocation Contract）

定义 Claude Code 和 Codex 双 harness 的调用模型，来源 mattpocock/skills `.agents/invocation.md`。

## 1. 双 harness 调用模型

### Claude Code

- `disable-model-invocation: true`：标记 user-invoked 技能
- `disable-model-invocation` 省略：标记 model-invoked 技能

### Codex

- `policy.allow_implicit_invocation: false`：标记 user-invoked 技能
- 省略该字段：标记 model-invoked 技能

### agents/openai.yaml

每个 `SKILL.md` 旁放 `agents/openai.yaml`，含 Codex UI 元数据：

- `interface.display_name`：技能显示名称
- `interface.short_description`：技能简短描述

## 2. 依赖表达

- 显式 `Call the Skill tool with "name"`
- 不使用 `/name` 风格的 hint
- user-invoked 技能不能被其他技能通过 Skill tool 调用（包括按名称）

## 3. 调用层级

```
user-invoked → model-invoked → model-invoked
     ↓              ↓              ↓
  grill-me     grilling     tdd
  ask-matt     researching  code-review
  wayfinder    prototype    domain-modeling
```

## 4. 完整契约矩阵

| 技能 | Invocation | 标记 | 调用者 |
|------|-----------|------|--------|
| grill-me | user-invoked | `disable-model-invocation: true` | 仅用户 |
| grilling | model-invoked | 省略 | AI + 用户 |
| tdd | model-invoked | 省略 | AI + 用户 |
| ask-matt | manual | `invocation: manual` | 仅用户 |
| wayfinder | manual | `invocation: manual` | 仅用户 |
| prototype | model-invoked | 省略 | AI + 用户 |
| research | model-invoked | 省略 | AI + 用户 |
| triage | manual | `invocation: manual` | 仅用户 |

## 适用边界

- 适用于所有 skill 文件的 frontmatter 和 agents/openai.yaml 设计
- 对本地 AGENTS.md/CLAUDE.md 体系和未来多 harness 扩展有架构参考价值

## 来源

- `records/T0450-0831-ontology-closed-loop-review/report.md`（来源 ID: T0450-0831-ontology-closed-loop-review）
- mattpocock/skills `.agents/invocation.md`