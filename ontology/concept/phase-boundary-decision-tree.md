---
schema: pdca.asset/v1
id: ontology:concept/phase-boundary-decision-tree
type: concept
layer: Knowledge
status: active
summary: Phase Boundary 五选项决策树：session 内阶段切换点的决策指引
relations:
  specializes:
  - ontology:concept/pdca-transition
attributes:
- name: applicability
  desc: 适用于所有 PDCA session 内阶段切换决策
  constraint: 见正文
  testable_signal: 检查 flow-do 收尾阶段是否输出 Phase Boundary 决策树；模型是否按序询问五个选项
---

# Phase Boundary Decision Tree（Phase Boundary 决策树）

session 内阶段切换点按序问五个选项，第一个 yes 获胜：

1. **能继续吗**（下一阶段要本阶段作 primary source）→ Continue
2. **上下文与后续无关** → /clear
3. **需要跨 harness/目录/同事/支线分叉** → /handoff
4. **任务可 AFK** → Subagent
5. **否则 /compact**（默认但非首选）

## 底层逻辑

一手源（信息全噪声大）/ 二手源（有损低噪空间大）交换表：只有留下的成本大于收益才付有损代价。mid-phase 永不决策。

## 原则

- 阶段切换是决策点，不是自动过渡
- 模型应在每个阶段切换时输出决策树
- 第一个 yes 获胜，不全部询问
- 只在留下成本大于收益时才付有损代价

## 边界

本决策树改变提问组织方式，不改变 Plan/Do/Check/Act 门禁判定逻辑。