---
schema: pdca.asset/v1
id: T0418-0830-pdca-flow-ontology-record
phase: check
source_ids: [migration-manifest-v2-t0418, ontology-validate-t0418, reference-audit-t0418, convergence-map-v3-t0418]
---

# T0418 结论：PDCA 流程本体化（0829 协调子流）

## 上下文

PDCA 工作流本身是 PDCA 本体的实体，但四个流程 `flows/flow-{plan,do,check,act}.md` 仅以 SKILL 文档存在，未成为本体实体；大量外部 PDCA 实体描述与决策记录散落于 `knowledge/pdca-flow/`（16 文件）、`knowledge/pdca-workflow/`（6 文件）与 `docs/adr/ADR-0032~0036`，与本体重叠且冗余。父任务 T0829 已建立"完整本体 + ontology-validate/ontology-check 机制"。本任务作为 T0829 协调子流，将 PDCA 流程本体化，并把外部 PDCA 描述/决策迁移进本体，复用既有机制、不重建。

## 假设与结果

- 假设：把四个流程建模为 `ontology:process/flow-*` 实体（specializes=ontology:concept/process，与既有 code-review-process 一致），并将外部知识逐主题并入流程实体或 supporting 概念节点、把 ADR 决策沉淀进本体，可使外部冗余描述消除且事实不丢失。
- 结果：新建 4 个流程实体 + 16 个支撑概念节点；`knowledge/pdca-flow/`、`knowledge/pdca-workflow/` 两目录已删除；ADR-0032~0036 决策已迁移进本体节点（背景并入对应「决策背景」段）并删除原 ADR 文件；全部新节点经 ontology-validate 校验通过。

## 分析

- **AC-1** ✅ 四个流程实体 `ontology/process/flow-{plan,do,check,act}.md` 创建，`type=process` 且 `specializes=[ontology:concept/process]`（与 code-review-process 一致），relations 关联对应 phase 实体与 gate，body 含权威描述与关键决策（migration-manifest-v2-t0418）
- **AC-2** ✅ `knowledge/pdca-flow/` 16 文件描述与决策迁移进本体（流程实体或 supporting 节点），引用审计无误后目录已删除（migration-manifest-v2-t0418 / reference-audit-t0418）
- **AC-3** ✅ `knowledge/pdca-workflow/` 6 文件迁移进相关本体节点（pdca-verdict / pdca-acceptance-criterion / pdca-task / pdca-continuous-improvement 等），引用审计无误后目录已删除（migration-manifest-v2-t0418 / reference-audit-t0418）
- **AC-4** ✅ ADR-0032~0036 决策沉淀进相关本体节点（pdca-architecture / ontology-creation-gate / ontology-validate / pdca-evidence / pdca-verdict / ontology-rule-* 等），原 ADR 文件已删除，背景并入对应节点「决策背景」段（migration-manifest-v2-t0418）
- **AC-5** ✅ 全部新节点经 `scripts/ontology-validate.py` 校验通过（退出码 0、无悬空引用、无环），复用 T0829 既有校验机制，未新建校验器（ontology-validate-t0418）
- **AC-6** ✅ grep 确认 `scripts/SKILL/flows/docs` 中对 `knowledge/pdca-flow/`、`knowledge/pdca-workflow/` 路径无残留引用；本体节点来源路径已去前缀、T0263 PRD 已更新指向本体 id；ADR-0032~0036 文件已删除且核心内容已在本体；仅历史 `pdca/journal/*.md` 保留溯源引用（不可变记录，按 AC-6 例外保留）（reference-audit-t0418 / migration-manifest-v2-t0418）

## 适用边界

- 流程实体是"知识图谱中的 process 节点"，不改变 `flows/flow-*.md` 的运行时 SKILL 行为；两轴独立（本体 type/specializes vs task.json 的 `meta.ontology_anchor`）。
- `docs/pdca-workflow-*.md` 等渲染视图保留为"非目标"（人类可读，不视为冗余描述）。
- ADR-0032~0036 已迁移决策至本体并删除原文件，其"背景/决策缘由"并入对应本体节点「决策背景」段；其余历史 ADR 不受影响。

## 下一轮建议

- 后续若有新 PDCA 元机制决策，直接沉淀进对应本体节点，必要时把旧描述/文档迁移后删除，避免再次散落。
- 0829 完成 tls 域试点后，可审视 `ontology/process/flow-*` 与领域流程实体是否需进一步关系补全（如 flow→领域 process 的 `relates_to`）。

## Verdict（建议，待用户确认固化）

- **outcome**: confirmed
- **reason**: 6 项 AC 全部满足，证据齐备（迁移清单、本体校验输出、引用审计），本体校验通过，外部冗余知识已迁移并删除，机制零新建。
- **verdict_id**: verdict-t0418-confirmed
- **at**: 2026-08-30T09:31:00+08:00
- 此区块由用户 `check_confirmation` 确认后写入 `task.json` `meta.verdict`，AI 不代签。
