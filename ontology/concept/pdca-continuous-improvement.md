---
schema: pdca.asset/v1
id: ontology:concept/pdca-continuous-improvement
type: concept
layer: Knowledge
summary: PDCA 是持续改进循环（act 后回到 plan），本工作流单任务生命周期则在 archive 终止
status: active
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:entity/phase-act
  - ontology:entity/phase-plan
---
# pdca-continuous-improvement

PDCA 的本质是**持续改进循环**，而非单向流水线（ASQ："a circle has no end… repeated again and again"；Wikipedia："implemented in spirals"）。

- **循环语义**：`act`（处理/标准化）完成后，应带着学到的经验**回到 `plan`** 开启新一轮改进。即 `plan → do → check → act → (新) plan` 无终点循环。
- **本工作流的双层建模**：
  - *方法论层*：PDCA 是环，由本概念承载 `act ↔ plan` 的循环关系。
  - *任务生命周期层*：单任务是有终点的流水线，`act` 之后进入运维扩展节点 `archive`（见 `ontology:entity/phase-archive`），任务因此终止；但方法论上的"下一轮 plan"对应于**新建任务**或在同一任务内发起新的 Grill/PRD 迭代。
- **为何不建成 `transition-act-plan` 边**：任务转换图必须保持无环（`ontology-validate` 禁止 CYCLE，且单任务生命周期须能终止）。故循环以**概念关系**表达，而非可执行的任务转换边。
