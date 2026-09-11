---
schema: pdca.asset/v1
id: ontology:concept/ask-matt
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/ask-matt/1.0.1
summary: 路由技能：根据用户描述推荐合适的 PDCA 入口
relations:
  specializes:
  - ontology:concept/router-skill
  relates_to:
  - ontology:concept/skill-invocation
  - ontology:concept/user-invoked
attributes:
- name: applicability
  desc: 适用于所有需要路由到合适 PDCA 入口的场景
  constraint: 见正文
  testable_signal: 检查新技能是否声明其针对的失效模式；治不了明确病的技能不应存在
---

# Ask Matt（路由技能）

根据用户描述推荐合适的 PDCA 入口。初次使用或不确定从哪开始时，从这里入手。

## 原则

- ask-matt 是用户入口路由技能，将用户描述送入 triage，由 triage 输出三个专业职责之一和四字段执行契约
- 路由基于 skill-invocation 机制，区分 user-invoked 和 model-invoked
- 路由结果必须是已存在的 manual entry
- 入口路由勿重复追问已确认的需求

## 输入映射

| 用户说 | 推荐入口 |
|--------|----------|
| "我想做一个新功能/新模块" | `/triage` → 职责与契约 → Plan |
| "有个 bug 要修" | `/triage` → 通常为 `ontology_projection`，以契约确认 |
| "调研/分析/了解一下 XXX" | `/triage` → 通常为 `ontology_modeling`，可选 `research` 工具 |
| "审查/Review 代码" | `/triage` → 通常为 `ontology_conformance_verification`，可选 `code-review` 工具 |
| "把需求写成技术文档" | `/triage` → 按本体目标选职责，文档写作作为契约动作 |
| "设计 XXX 的架构" | `/triage` → 通常为 `ontology_modeling`，可选 `design-it-twice` 工具 |
| "有个大工程要做" | `/wayfinder` 先画地图 |
| "代码结构需要改进" | `/codebase-design` 深度审查 |
| "帮我理清思路/对齐目标" | `/grill` 追问门禁 |
| "上次做了一半的工作" | 查 archives 恢复 |
| "我想了解这个项目/代码库" | 搜索 `$PDCA_HOME/ontology/domain/` + `$PDCA_HOME/records/` |

## 验证

- 路由目标必须是已声明的 manual entry
- alias 必须解析到现有 manual entry
- 入口文档暴露的 alias 与 contract 必须双向一致
- triage 输出的 `ontology_role` 必须是三个专业职责之一，`execution_contract` 必须恰含 `work_product`、`required_actions`、`constraints`、`testable_signal`
