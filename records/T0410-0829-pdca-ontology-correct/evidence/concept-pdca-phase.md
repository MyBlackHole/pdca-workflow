---
schema: pdca.asset/v1
id: ontology:concept/pdca-phase
type: concept
layer: Knowledge
summary: PDCA 阶段元概念（经典四阶段 plan/do/check/act；archive 为工作流运维扩展）
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-phase

PDCA（Plan-Do-Check-Act，又称 Deming Cycle / Shewhart Cycle）的**阶段**元概念。

## 经典四阶段（PDCA 方法论本身）
- **plan（计划）**、**do（执行）**、**check（检查）**、**act（处理/标准化）** 四阶段（ASQ 称 four-step model；Wikipedia 列出此四阶段）。
- 这四个是 PDCA 方法论的**全部**阶段。**archive 不是 PDCA 方法论阶段**。

## archive 的定位（运维扩展，非方法论阶段）
- `phase-archive` 是**本工作流（pdca-workflow）**在单任务生命周期末尾加入的**运维扩展**节点，用于把已完成任务移出活跃区、保留不可变记录。
- 它**不计入** PDCA 方法论阶段集；其 `specializes: pdca-phase` 仅表示"它借用了阶段这一元概念的位置"，正文见 `ontology:entity/phase-archive`。

## PDCA 是环，不是线（见 pdca-continuous-improvement）
- 经典 PDCA 是持续改进**循环**：act 之后应回到 plan 开启新一轮（"a circle has no end… repeated again and again"，ASQ）。
- 本工作流把单任务生命周期建模为**有终点的流水线**（act→archive）；方法论层面的循环由 `ontology:concept/pdca-continuous-improvement` 承载。

## 术语注记：PDCA 与 PDSA
- Deming 本人更偏好 **PDSA**（Plan-Do-**Study**-Act），因 Study 强调深度学习与理论提炼；PDCA 的 Check（检查）是日方参与者简化后的通俗变体（Wikipedia、6Sigma）。
- 两者等价表达同一改进循环；**本工作流沿用 PDCA 命名**。

