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
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-wayfinding-chart/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

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

## Type
research | prototype | grilling | task

## Blocked By
- <阻塞此票的票 ID>

## Status
open | in-progress | resolved
```

### 5. 并行执行 Research 票
`agent.spawn` 可用时通过当前环境 Adapter 并行解决 research 票；不可用时由主 session 按风险优先级顺序执行。

## 已知坑

- 由 wayfinder 委托加载，勿在 flow 中直接触发；绕过委托会破坏调用契约。
