---
schema: pdca.asset/v1
id: ontology:concept/skill-mechanics-detail
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-mechanics-detail/1.0.0
summary: 技能机制详细说明：frontmatter、invocation 选择和路由技能的详细机制
relations:
  specializes:
  - ontology:concept/skill-mechanics
  relates_to:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有需要详细描述技能机制的场景
  constraint: 见正文
  testable_signal: 检查技能 frontmatter 是否完整、invocation 是否合法
- name: trigger_phrase
  desc: 触发短语
  constraint: 至少声明一个
  testable_signal: 检查是否包含声明式触发短语
- name: trigger_context
  desc: 触发条件
  constraint: 见正文
  testable_signal: 检查触发条件是否覆盖所有预期场景
---

# Skill Mechanics Detail（技能机制详细说明）

技能机制的详细说明，对应 mattpocock/skills 的 SKILL-MECHANICS.md。

## frontmatter

每个技能必须声明：
- `name`：技能名称
- `description`：技能描述
- `invocation`：调用方式（manual 或无标记）

## invocation 选择

- user-invoked：`invocation: manual`，仅用户触发
- model-invoked：无 invocation 标记，AI 可自主触发
- 路由技能：user-invoked，可调用 model-invoked

## 路由技能

- 一个 user-invoked 技能命名其他技能及触发时机
- alias 必须解析到现有 manual entry
- 入口文档暴露的 alias 与 contract 必须双向一致