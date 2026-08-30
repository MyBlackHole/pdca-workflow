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
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
---

-----|------|------|
| **Research** | AFK | 读文档/代码/知识库，输出事实 |
| **Prototype** | HITL | 做粗糙原型验证设计假设 |
| **Grilling** | HITL | 与用户对话逐条决策，联动 domain-modeling |
| **Task** | 混合 | 必须在决策前完成的手工工作 |

## 方向判断

- **已有地图**（`$PDCA_HOME/pdca/tasks/wayfinder-*/MAP.md` 存在）→ 加载 `$PDCA_HOME/skills/wayfinding-work/SKILL.md`
- **无地图** → 加载 `$PDCA_HOME/skills/wayfinding-chart/SKILL.md` 绘制新地图

## 已知坑

- 拆解粒度以"多 session 可推进"为界，勿过度拆解成碎片化决策票。
