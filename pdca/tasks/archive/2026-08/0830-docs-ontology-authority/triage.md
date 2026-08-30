# T0422 triage

- 触发：用户要求"审查 docs/ 目录与其他多余内容，本体必须成为知识的唯一权威来源"。即 docs/ 中重复本体的内容须迁移进本体或删除，使本体成为唯一权威。
- 现状：本体已有 46 concept + 5 process + 21 entity 节点，覆盖 PDCA 全流程（pdca-architecture/task/evidence/gate*/phase/transition、flow-* 等）。docs/ 含 7 个文档 + renders/ 渲染产物。
- docs/ 逐项分类（与本体重叠度）：

  A 类【叙事/事实与本体重叠，可析出或删除】
  - `docs/capability-protocol.md`（23 行）：能力协议，CONTEXT「能力协议」+ 本体能力相关节点已覆盖。
  - `docs/project-architecture-design.md`（443 行）：六维缺陷与方案，重叠 pdca-architecture/pdca-task/pdca-evidence/pdca-gate*/pdca-phase/pdca-transition/flow-*。
  - `docs/pdca-workflow-full.md`、`docs/pdca-workflow-detail.md`：工作流叙述/流程图，重叠 ontology/process/flow-* + pdca-phase/transition。

  B 类【生成渲染产物（可再生成，非权威内容）】
  - `docs/pdca-workflow-full.mmd`、`.svg`、`docs/pdca-workflow-full.svg`、`docs/renders/*.mmd`、`docs/renders/*.svg`（共 7 个图文件）。

  C 类【关于本体本身的元指南】
  - `docs/ONTOLOGY_GUIDE.md`（13KB）：本体使用指南。ADR-0033 曾明确"指南置于 docs/，不放入 ontology/ 以免破坏 ontology-validate 扫描"。属元文档，非知识内容本身。

- 其他多余内容（候选，待确认是否纳入）
  - `knowledge/` 下冗余桩文件：约 16+ 个"已按 ADR-0030 物理归并至本体库"的 redirect 桩（T0420 已清引用，但桩文件本身仍在）；若本体为唯一来源，这些桩属多余。
  - 活动文件对 docs/ 的引用（AGENTS.md、flows/flow-do/SKILL.md、CONTEXT.md、ontology 节点、skills/* 等共 9 个文件）需改写指向本体节点。

- 风险：project-architecture-design.md 含大量叙述性解释，全量迁入本体工作量较大；需先明确"迁移 vs 删除 vs 保留为派生概览"的处置。
- 验收判定：docs/ 下与本体重叠的内容已迁移或删除；全仓 docs/ 引用改写为本体节点；本体校验通过、islands=0。
