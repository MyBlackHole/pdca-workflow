---
name: wayfinder
description: |
  将大型需求拆解为多 session 可推进的决策地图（map）。
  每 session 解决一张决策票（ticket），逐步清空地图直到路径清晰。
disable-model-invocation: true
---

# Wayfinder — 多 Session 大型规划

## 概念

> 一个模糊的大想法来了——大到一次 AI session 装不下，路径被迷雾笼罩。
> Wayfinding 就是找到这条路，而不是莽向终点。

输出一张 **地图（map）**：一个 `pdca/tasks/wayfinder-<name>/` 目录，包含：

```
pdca/tasks/wayfinder-<name>/
├── MAP.md              ← 地图本体：destination + 决策清单 + 迷雾 + 范围外
├── tickets/            ← 决策票
│   ├── 01-<slug>.md
│   ├── 02-<slug>.md
│   └── ...
```

每 session 解决一张票，更新地图。地图清空时路径可见。

## Ticket 类型

| 类型 | 模式 | 描述 |
|------|------|------|
| **Research** | AFK | 读文档/代码/知识库，输出事实 |
| **Prototype** | HITL | 做粗糙原型验证设计假设 |
| **Grilling** | HITL | 与用户对话逐条决策，联动 domain-modeling |
| **Task** | 混合 | 必须在决策前完成的手工工作 |

## 流程

### 1. 绘制地图（Chart）

用户带着一个模糊的大想法进入。

1. **确定 Destination** — 地图找到什么。"到达终点时看到什么？"
2. **广度优先 Grilling** — 扫射整个空间，找到所有开放决策，不深挖任何一条线
3. **创建 MAP.md**：

```markdown
# Wayfinder Map: <名称>

## Destination
<到达终点时的状态。一条线，每个 session 开工前先读。>

## Notes
<领域；每 session 应加载的技能；偏好>

## Decisions So Far
- [<closed ticket title>](link) — <一行摘要>

## Not Yet Specified
- <能看出会来但还不能开票的决策>

## Out of Scope
- <已排除在此次 effort 之外的工作>
```

4. **创建可指定的 ticket** 写入 `tickets/01-<slug>.md`...，每张票一个文件：

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

5. **并行执行 Research 票** — 用子代理并行解决 research 票

### 2. 推进地图（Work）

用户带着一个地图 URL/路径进入。

1. **读 MAP.md** — 看 destination 和 decisions-so-far
2. **选票** — 取 frontier 票（open + unblocked）
3. **执行** — 按 ticket type 对应的技能执行
4. **记录** — 更新 ticket 为 `resolved`，追加 decisions-so-far 到 MAP.md
5. **消雾** — 如果此票揭示了新方向，开新票或移出 not-yet-specified

**规则**：每 session 只解决一张票（research 除外可并行）。

## 与现有 PDCA 的关系
- wayfinder 不是 PDCA 的替代，而是 Plan 的超集：当需求太大时才触发
- 地图清空后，最终输出可进入正常 PDCA Plan → Do → Check → Act