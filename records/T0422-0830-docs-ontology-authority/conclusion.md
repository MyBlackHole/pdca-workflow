# T0422 结论：审查 docs/ 与多余内容，确立本体为知识唯一权威来源

## 上下文
T0418~T0421 已删除 `docs/adr/`、清理 `knowledge/` 与活动文件中的已删 ADR 悬空引用。T0422 在此基础上进一步审查 `docs/` 目录与 `knowledge/` 冗余桩，将重复本体的内容析出进本体或删除，使本体成为知识的唯一权威来源，`docs/` 目录整体退出使用。

## 假设与结果
- Plan 假设：docs/ 下 7 个文档 + renders/ 渲染产物与本体高度重叠，可迁移或删除；knowledge/ 含 16 个重定向桩；9 个活动文件含指向 docs/ 的实时引用。
- 结果：8 项 AC 全部完成；`ontology-validate.py` 通过、`islands=0`（nodes:89/edges:189）；8 条证据已登记；`validate-convergence` valid:true；全仓（排除 records/journal/tasks）无指向已删 docs/ 文件的实时引用；`docs/` 目录已整体删除。

## 分析（逐 AC 判定）
- **AC-1 ✅**：`capability-protocol` 关键事实析出进新建 `ontology/concept/capability-protocol.md`，删除 `docs/capability-protocol.md`。（证据 ev-cap-protocol）
- **AC-2 ✅**：`project-architecture-design` 的六维缺陷/五层架构/知识沉淀管线析出进 `pdca-architecture.md`、`pdca-continuous-improvement.md`，删除原文。（证据 ev-architecture）
- **AC-3 ✅**：`pdca-workflow-full/detail` 的生命周期要点析出进 `pdca-phase.md`，删除两个文档。（证据 ev-workflow）
- **AC-4 ✅**：删除 `docs/renders/*`（10 文件）、`docs/pdca-workflow-full.svg/.mmd`。（证据 ev-renders）
- **AC-5 ✅**：`ONTOLOGY_GUIDE` 的节点编写约定/流程消费/演进历史并入 `ontology/README.md`，删除 `docs/ONTOLOGY_GUIDE.md`。（证据 ev-readme）
- **AC-6 ✅**：删除 `knowledge/` 下 16 个含「物理归并至本体库」标记的 redirect 桩，保留真实知识文件。（证据 ev-knowledge-stubs）
- **AC-7 ✅**：9 个活动文件的 docs/ 实时引用改写为本体节点或移除（`AGENTS.md`/`flow-do`/`pdca.md`/`ontology-creation-gate`/`ontology-asset`/`pdca-architecture-review-metrics`/`CONTEXT.md`/`code-review`/`context-orchestration`）。（证据 ev-refs-rewritten）
- **AC-8 ✅**：本体校验通过、islands=0、证据+收敛映射登记、`validate-convergence` valid:true、无 docs/ 实时引用。（证据 ev-ontology-validate）

## 失败原因
无（全部 AC 达成，未触发 rejected/partial 分支）。

## 适用边界
- 本体节点中保留「原 docs/... 来源」历史注记，仅作来源溯源，不构成对 docs/ 的实时引用。
- `records/`、`pdca/journal/`、`pdca/tasks/`（含 archive）中的既有历史文档引用属不可变记录，不在本次清理范围。
- `records/T0272-0815-self-audit/health-audit.md` 为用户既有未提交改动（T0272 自审计），始终排除于任何提交之外。

## 下一轮建议
- 后续新建文档/指南须直接落 `ontology/` 或 `knowledge/`，不再新建 `docs/` 目录。
- `skills/drafts/` 下草稿技能（如 context-orchestration）可纳入后续本体化/规范化审查。
- 可考虑对 `knowledge/` 真实文件做一次"是否仍有与本体节点重复"的轻量复核。

## 已知坑
- `docs/` 已整体删除；凡脚本/模板/README 中提及 `docs/` 输出路径者须改指 `ontology/` 或 `knowledge/`。
- git 提交须排除 `health-audit.md`（T0272 既有未提交改动），否则会误带用户私有内容。

## 判定
- verdict.outcome: **confirmed**
- reason: 8 项 AC 全部达成，本体校验通过且无孤岛，证据链与收敛映射机器可复核，全仓无 docs/ 实时引用残留。
- verdict_id: T0422-confirmed-2026-08-30
- at: 2026-08-30T10:54:30+08:00
