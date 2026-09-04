---
schema: pdca.asset/v1
id: ontology:entity/phase-act
type: entity
layer: Knowledge
summary: PDCA act 阶段
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/phase-act/1.0.0
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-act

PDCA 的**处理/标准化**阶段（经典四阶段之一），从结论到知识积累与处置。

- **科学方法内核**：Act 是"**依据 Check 结论采纳或放弃**"——confirmed 则把有效变更**标准化/固化**为可复用资产（知识/模式/规则），rejected 则废弃并保留教训，partial 则提炼有效部分并派生跟进。学习被沉淀，才完成一次科学方法闭环（对应经典 PDCA 的"act on what was learned"）。
- **目的**：把 confirmed 结论沉淀为可复用知识/资产，完成处置；并把学到的经验带回下一轮改进。
- **进入条件**：`meta.phase=act`，`records/<record-id>/conclusion.md` 存在。
- **关键活动**：Grill 沉淀质量 → 知识沉淀（优先关联既有 ontology 节点）→ 记录 disposition → 架构改进（发现本体缺口则建补强任务）→ handoff → 追加 journal → 提交（含 disposition）→ 归档（`archive/` + git mv）。
- **与 PDCA 循环的关系**：方法论上 `act` 之后应回到 `plan` 开启新一轮（见 `ontology:concept/pdca-continuous-improvement`）；本工作流把单任务生命周期建模为终止于 `archive`，故"下一轮 plan"对应于新建任务或在任务内发起新的 Grill/PRD 迭代。
- **退出**：任务已归档，`meta.disposition` 齐备。
- **对应流程**：`ontology/process/flow-{plan,do,check,act}.md`。

