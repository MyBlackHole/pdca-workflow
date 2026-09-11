---
schema: pdca.asset/v1
id: ontology:domain/skill-wayfinder
name: wayfinder
summary: Navigate and find the right path in complex PDCA workflows.
description: |
  将大型需求拆解为多 session 可推进的决策地图。
  Session 入口：已有地图时加载 wayfinding-work，无地图时加载 wayfinding-chart。

invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/skill-wayfinder/1.0.1
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
    - ontology:concept/phase-boundary-decision-tree
    - ontology:concept/skill-mechanics
  testable_signal: "运行 grep -q 'Wayfinder — 决策地图导航' ontology/domain/pdca/skill-wayfinder.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


# Wayfinder — 决策地图导航

将大型需求拆解为多 session 可推进的决策地图。每张 ticket 声明一个 `ontology_role`、四字段 `execution_contract` 和交互模式；`research`、`prototype`、`grilling` 只可写入 `required_actions` 作为工具动作。

## Ticket 执行约束

每个 ticket 根据契约是否需要真实用户输入声明 **HITL**（human in the loop）或 **AFK**（agent alone）：

- **HITL ticket** 只通过 live exchange 解决——grilling agent 如果自己回答了问题，就违反了 HITL
- **AFK ticket** 可由 agent 独立完成

### HITL/AFK 判定规则

| 契约条件 | 模式 | 说明 |
|-------------|------|------|
| `required_actions` 只含可独立完成的检索、原型制作或事实核验 | AFK | Agent 可独立产出并登记证据 |
| `required_actions` 含 grilling、方向选择或用户偏好裁决 | HITL | 必须通过 live exchange 解决 |
| 契约同时含独立动作与用户裁决 | 混合 | 拆成有依赖边的独立 ticket |

### HITL 约束

- HITL ticket 只通过 live exchange 解决
- grilling agent 如果自己回答了问题，就违反了 HITL
- HITL ticket 必须通过 live exchange 解决，不可由 agent 自主回答

### AFK 约束

- AFK ticket 可由 agent 独立完成
- 不需要 live exchange
- 可并行执行多个 AFK ticket

## 方向判断

- **已有地图**（`$PDCA_HOME/pdca/tasks/wayfinder-*/MAP.md` 存在）→ 加载 `$PDCA_HOME/skills/wayfinding-work/SKILL.md`
- **无地图** → 加载 `$PDCA_HOME/skills/wayfinding-chart/SKILL.md` 绘制新地图

## 已知坑

- 拆解粒度以"多 session 可推进"为界，勿过度拆解成碎片化决策票。
- HITL ticket 必须通过 live exchange 解决，不可由 agent 自主回答。
- HITL/AFK 判定是 wayfinder 的核心机制，但不得反向成为任务职责或阶段路由。
