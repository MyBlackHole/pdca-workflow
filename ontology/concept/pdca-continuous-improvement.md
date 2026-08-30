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

## 决策背景（原 ADR-0004：Flow Issue 使用独立不可变事件文件）
- 背景：T0159 需把 PDCA 机制问题作为聚合/诊断/改进的事实输入；旧 flow-audit.json 整体更新 latest/attempts，不满足单事件不可变，整文件摘要每次变化。
- 决策：每个 occurrence 使用独立 JSON 文件（独占创建保证幂等/不可覆盖、并发互不修改、稳定路径与摘要、损坏隔离）；聚合视图随算法升级重建；符合 records/ 不可变约束。

## 知识沉淀管线（原 docs/project-architecture-design.md §3.2）

改进闭环的载体是知识资产的逐级提炼，每级同步更新 `manifest.jsonl`：

```
原始事实 → Evidence（register-evidence 登记，manifest.jsonl）
        → Experience（records/ 中的 conclusion.md）
        → Knowledge（ontology/domain/ 下的 .md，由 flow-act 步骤 2 提炼）
        → Skill（skills/ 下的 SKILL.md，由 writing-skills 创建）
```

- `records/` 下的文件创建后不可修改（不可变记录约束），保证事实源稳定可追溯。
- flow-act 步骤 2 负责从经验提炼 Knowledge；稳定知识可进一步沉淀为 Skill，形成可跨会话/跨任务复用的资产。
