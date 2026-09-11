---
schema: pdca.asset/v1
id: ontology:domain/skill-wayfinding-chart
name: wayfinding-chart
summary: Create wayfinding charts for navigation in PDCA workflows.
description: 绘制 Wayfinder 决策地图。由 wayfinder 委托加载，不直接调用。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/skill-wayfinding-chart/1.0.2
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
  testable_signal: "运行 grep -q 'Wayfinding — 绘制地图（Chart）' ontology/domain/pdca/skill-wayfinding-chart.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


---
name: wayfinding-chart
description: 绘制 Wayfinder 决策地图。由 wayfinder 委托加载，不直接调用。
---

# Wayfinding — 绘制地图（Chart）

### 1. 确定 Destination
"到达终点时看到什么？"——一条线，每个 session 开工前先读。

### 2. 广度优先 Grilling
扫射整个空间，找到所有开放决策，不深挖任何一条线。联动 `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`。

### 3. 创建 MAP.md

```markdown
# Wayfinder Map: <名称>

## Destination
<到达终点时的状态>

## Notes
<领域；每 session 应加载的技能；偏好>

## Decisions So Far
- [<closed ticket title>](link) — <一行摘要>

## Not Yet Specified
- <能看出会来但还不能开票的决策>

## Out of Scope
- <已排除在此次 effort 之外的工作>
```

### 4. 创建 Ticket

```markdown
# <标题>

## Question
<此票解决的决策或调研问题>

## Ontology Role
ontology_modeling | ontology_projection | ontology_conformance_verification

## Execution Contract
- work_product: <本票产物>
- required_actions: [<可选工具或动作>]
- constraints: [<边界与禁止项>]
- testable_signal: <可验证完成信号>

## Blocked By
- <阻塞此票的票 ID>

## Status
open | in-progress | resolved
```

### 5. 按 ready-set 执行票
每张可执行票都是独立 PDCA 任务，并行性只由依赖边与 ready-set 决定。当前任务的协调 Agent 必须通过 Adapter 调用 `agent.spawn`，一次性启动一对一的全新子 Agent/子智能体上下文后进入 `suspended_waiting_agent`；子 Agent 按 `ontology_role` 与 `execution_contract` 自主执行。恢复后只读当前任务持久化产物并执行 `ontology_conformance_verification`，不得检查其他任务。能力不可用时 fail-closed，不得由协调 Agent 或既有子 Agent 执行。

## 已知坑

- 由 wayfinder 委托加载，勿在 flow 中直接触发；绕过委托会破坏调用契约。
