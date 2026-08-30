# T0422 PRD：审查 docs/ 与多余内容，确立本体为知识唯一权威来源

## 背景
T0418~T0421 已删除 `docs/adr/`、清理 knowledge/ 与活动文件中的已删 ADR 悬空引用。现按"本体必须成为知识唯一权威来源"原则，审查 `docs/` 目录与 knowledge/ 冗余桩，将重复本体的内容析出进本体或删除，使 `docs/` 不再作为权威来源。

## 目标
将 `docs/` 中重复本体的内容迁移进本体并删除原文；删除生成产物与冗余桩；`ONTOLOGY_GUIDE` 并入 `ontology/README`；全仓对 `docs/` 的引用改写为本体节点。

## 验收标准
- [ ] AC-1：`docs/capability-protocol.md` 关键事实析出进新建 `ontology/concept/capability-protocol.md` 后删除原文。
- [ ] AC-2：`docs/project-architecture-design.md` 关键事实析出进对应本体节点（pdca-architecture/pdca-task/pdca-evidence/pdca-gate*/pdca-phase/pdca-transition/flow-* 等，补充「决策背景/说明」段）后删除原文。
- [ ] AC-3：`docs/pdca-workflow-full.md`、`docs/pdca-workflow-detail.md` 关键事实析出进 `ontology/process/flow-*` 与 pdca-phase/transition 节点后删除。
- [ ] AC-4：删除生成渲染产物 `docs/renders/*`、`docs/pdca-workflow-full.svg`、`.mmd`。
- [ ] AC-5：`docs/ONTOLOGY_GUIDE.md` 内容并入 `ontology/README.md` 后删除原文。
- [ ] AC-6：删除 `knowledge/` 下含"物理归并至本体库"标记的 redirect 桩（约 16+），保留真实知识文件。
- [ ] AC-7：活动文件（AGENTS.md、CONTEXT.md、flows/flow-do/SKILL.md、ontology 节点、skills/* 等）对 `docs/` 的引用全量改写为本体节点。
- [ ] AC-8：`ontology-validate.py` 通过、islands=0；登记证据 + 收敛映射，`validate-convergence.py` valid:true；全仓（排除 records/journal/tasks）无指向已删 `docs/` 文件的引用。

## 关联本体节点
- 新建：ontology:concept/capability-protocol
- 增强：ontology:concept/pdca-architecture、pdca-task、pdca-evidence、pdca-gate*、pdca-phase、pdca-transition、ontology/process/flow-*
- 元指南：ontology/README.md（并入 ONTOLOGY_GUIDE）
