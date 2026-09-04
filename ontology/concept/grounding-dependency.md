---
schema: pdca.asset/v1
id: ontology:concept/grounding-dependency
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/grounding-dependency/1.0.0
summary: Grounding 依赖图：概念必须 grounding 后才能被后续块依赖
relations:
  specializes:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有知识资产和长文档的分段生成
  constraint: 见正文
  testable_signal: 检查知识资产中每个概念是否声明了 requires/grounds；候选续写是否仅从当前 grounded 集合可达
---

# Grounding Dependency（Grounding 依赖图）

概念必须 grounding 后才能被后续块依赖——读者带来（prerequisite）或先前块引入（introduced）。每 beat 声明 requires/grounds 两组概念，候选续写只能从当前 grounded 集合可达。是"grilling session inverted"。

## 原则

- 每个概念必须声明 `requires`（读者带来）或 `grounds`（先前块引入）
- 候选续写只能从当前 grounded 集合可达
- 选择空间被依赖图机械约束
- 未 grounding 的概念不得被后续块依赖

## 适用场景

- 长文档/课程的分段生成
- 知识资产的分层构建
- 技能引用的概念链

## 边界

Grounding 依赖图是写作方法论，不是自动检查；它约束选择空间而非替代人工判断。