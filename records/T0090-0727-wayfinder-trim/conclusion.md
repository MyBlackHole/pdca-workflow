---
schema: pdca.asset/v1
id: T0090-0727-wayfinder-trim
layer: experience
summary: 精简 wayfinder 为薄壳 + 两个 model-invoked 体
tags: [wayfinder, skill, simplification]
---

# 结论: T0090 — 精简 wayfinder

## 目标
将 101 行的 wayfinder 拆分为 36 行薄壳 + wayfinding-chart/work 两个 model-invoked 体。

## 结果
- wayfinder 缩小到 36 行，仅保留路由逻辑
- wayfinding-chart（绘制决策地图）和 wayfinding-work（推进地图）作为独立技能
