---
name: wayfinder
description: |
  将大型需求拆解为多 session 可推进的决策地图。
  Session 入口：已有地图时加载 wayfinding-work，无地图时加载 wayfinding-chart。
invocation: manual
---

# Wayfinder — 多 Session 大型规划

> 一个模糊的大想法来了——大到一次 AI session 装不下，路径被迷雾笼罩。
> Wayfinding 就是找到这条路，而不是莽向终点。

输出一张**地图（map）**：

```
pdca/tasks/wayfinder-<name>/
├── MAP.md              ← 地图本体：destination + 决策清单 + 迷雾 + 范围外
├── tickets/            ← 决策票
│   ├── 01-<slug>.md
│   ├── 02-<slug>.md
│   └── ...
```

Ticket 类型：

| 类型 | 模式 | 描述 |
|------|------|------|
| **Research** | AFK | 读文档/代码/知识库，输出事实 |
| **Prototype** | HITL | 做粗糙原型验证设计假设 |
| **Grilling** | HITL | 与用户对话逐条决策，联动 domain-modeling |
| **Task** | 混合 | 必须在决策前完成的手工工作 |

## 方向判断

- **已有地图**（`$PDCA_HOME/pdca/tasks/wayfinder-*/MAP.md` 存在）→ 加载 `$PDCA_HOME/skills/wayfinding-work/SKILL.md`
- **无地图** → 加载 `$PDCA_HOME/skills/wayfinding-chart/SKILL.md` 绘制新地图