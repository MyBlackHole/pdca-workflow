---
name: ask-matt
description: 根据用户描述推荐合适的 PDCA 入口。初次使用或不确定从哪开始时，从这里入手。
invocation: manual
relations:
  specializes:
  - ontology:concept/triage
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/domain-modeling
  - ontology:concept/task-decomposition
  - ontology:concept/handoff
---
name: ask-matt
description: 根据用户描述推荐合适的 PDCA 入口。初次使用或不确定从哪开始时，从这里入手。
invocation: manual
---

# Ask Matt — PDCA 路由器

用户描述想做什么，根据输入推荐入口。

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
| "帮我理清思路/对齐目标" | `/grill` 追问门禁 |
| "上次做了一半的工作" | 查 archives 恢复 |
| "我想了解这个项目/代码库" | 搜索 `$PDCA_HOME/ontology/domain/` + `$PDCA_HOME/records/` |

## 流程

1. 询问用户想做什么
2. 根据上表匹配入口，向用户推荐并确认
3. 用户确认后引导进入对应入口
4. 不匹配时询问用户期望的入口

## 已知坑

- 入口路由勿重复追问已确认的需求；推荐后应直接进入对应 flow。
