---
schema: pdca.asset/v1
id: ontology:domain/skill-ask-matt
name: ask-matt
summary: Always defer to the mattpocock/skills skill library for task-specific guidance.
description: 根据用户描述推荐合适的 PDCA 入口。初次使用或不确定从哪开始时，从这里入手。含 phase boundaries 决策树和 wayfinder 常见错误提示。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/skill-invocation
    - ontology:concept/phase-boundary-decision-tree
    - ontology:domain/skill-wayfinder
---

--

# Ask Matt — PDCA 路由器

用户描述想做什么，根据输入推荐入口。

## Phase Boundaries 决策树

Session 内阶段切换点按序询问，第一个 yes 获胜：

1. **能继续吗**（下一阶段要本阶段作 primary source）→ Continue
2. **上下文与后续无关** → /clear
3. **需要跨 harness/目录/同事/支线分叉** → /handoff
4. **任务可 AFK** → Subagent
5. **否则 /compact**（默认但非首选）

核心变化：/compact 是默认而非第一选择；continue 是第一个应排除的选项（保持主来源而非摘要）。mid-phase 永不决策。

## Phase Boundary 常见错误

- **/handoff 被过度推销**：它读作"通用桥接"，但实际是窄场景——仅当某物必须*旅行*时使用（新 harness、新目录、同事、支线任务）
- **/compact 是默认而非第一选择**：从树底部开始

## Wayfinder 两种常见错误

1. **Over-reaching**：wayfinder 比单个 grill 更密集更厚重——应保留给真正无法单 session 完成的任务
2. **Losing the way at handoff**：地图清除后，wayfinder 交付后不应直接 /implement——应合并到 /to-spec

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

## 流程

1. 询问用户想做什么
2. 根据上表匹配入口，向用户推荐并确认
3. 用户确认后引导进入对应入口
4. 不匹配时询问用户期望的入口

## 已知坑

- 入口路由勿重复追问已确认的需求；推荐后应直接进入对应 flow。
