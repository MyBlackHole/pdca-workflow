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
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-wayfinder/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
    - ontology:concept/phase-boundary-decision-tree
    - ontology:concept/skill-mechanics
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Wayfinder — 决策地图导航

将大型需求拆解为多 session 可推进的决策地图。Ticket 4类 `wayfinder:research/prototype/grilling/task` 分 HITL/AFK（对齐 mattpocock/skills wayfinder label）。

## Ticket 分类

每个 ticket 类型分类为 **HITL**（human in the loop）或 **AFK**（agent alone）：

- **HITL ticket** 只通过 live exchange 解决——grilling agent 如果自己回答了问题，就违反了 HITL
- **AFK ticket** 可由 agent 独立完成

### HITL/AFK 分类规则

| Ticket 类型 | 分类 | 说明 |
|-------------|------|------|
| Research | AFK | 读文档/代码/知识库，输出事实 |
| Prototype | HITL | 做粗糙原型验证设计假设 |
| Grinding | HITL | 与用户对话逐条决策，联动 domain-modeling |
| Task | 混合 | 必须在决策前完成的手工工作 |
| Triage | HITL | 分类 incoming tasks，需人工判断 |
| Wayfinder | HITL | 画决策地图，需人工确认方向 |
| To-questionnaire | AFK | 发送问卷，可异步完成 |
| Wait-wait | AFK | 一句话纠偏，可快速完成 |

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
- HITL/AFK 分类是 wayfinder 的核心机制——分类错误会导致 ticket 执行方式不当。