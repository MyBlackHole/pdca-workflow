---
schema: pdca.asset/v1
id: ontology:entity/phase-act
type: entity
layer: Knowledge
summary: PDCA act 阶段
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-act

PDCA 的改进阶段：从结论到知识积累与归档。

- **目的**：把 confirmed 结论沉淀为可复用知识/资产，完成处置并归档。
- **进入条件**：`meta.phase=act`，`records/<record-id>/conclusion.md` 存在。
- **关键活动**：Grill 沉淀质量 → 知识沉淀（优先关联既有 ontology 节点）→ 记录 disposition → 架构改进（发现本体缺口则建补强任务）→ handoff → 追加 journal → 提交（含 disposition）→ 归档（`archive/` + git mv）。
- **退出**：任务已归档，`meta.disposition` 齐备。
- **对应流程**：`flows/flow-act/SKILL.md`。

