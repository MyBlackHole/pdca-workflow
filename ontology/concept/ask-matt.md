---
schema: pdca.asset/v1
id: ontology:concept/ask-matt
type: concept
layer: Knowledge
status: active
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

- ask-matt 是用户入口路由技能，将用户描述映射到具体的 PDCA 入口
- 路由基于 skill-invocation 机制，区分 user-invoked 和 model-invoked
- 路由结果必须是已存在的 manual entry
- 入口路由勿重复追问已确认的需求

## 输入映射

| 用户说 | 推荐入口 |
|--------|----------|
| "我想做一个新功能/新模块" | `/triage` → Plan → Do |
| "有个 bug 要修" | `/triage` → Plan(bugfix) → Do |
| "调研/分析/了解一下 XXX" | 直接创建 research 类型 task |
| "审查/Review 代码" | 直接创建 review 类型 task |
| "把需求写成技术文档" | 直接创建 documentation 类型 task |
| "设计 XXX 的架构" | 直接创建 design 类型 task |
| "有个大工程要做" | `/wayfinder` 先画地图 |
| "代码结构需要改进" | `/codebase-design` 深度审查 |
| "帮我理清思路/对齐目标" | `/grill` 追问门禁 |
| "上次做了一半的工作" | 查 archives 恢复 |
| "我想了解这个项目/代码库" | 搜索 `$PDCA_HOME/ontology/domain/` + `$PDCA_HOME/records/` |

## 验证

- 路由目标必须是已声明的 manual entry
- alias 必须解析到现有 manual entry
- 入口文档暴露的 alias 与 contract 必须双向一致