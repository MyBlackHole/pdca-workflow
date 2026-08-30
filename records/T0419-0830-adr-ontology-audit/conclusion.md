---
schema: pdca.asset/v1
id: T0419-0830-adr-ontology-audit
phase: check
source_ids: [t0419-migration, t0419-reference-v2, t0419-validate, t0419-convergence-v2]
---

# T0419 结论：docs/adr/ 全量迁移/删除与引用改写

## 上下文

T0418 收尾时发现 ADR-0032~0036 已可迁移进本体并删除，用户进一步指出 `docs/adr/` 整体多余。审计确认：目录 32 个 ADR 分两类——A 组 8 个 PDCA 元工作流 ADR（决策多数已有对应本体节点），B 组 24 个外部子系统 ADR（rpc/report/lmdb/small-file/backup/handshake 等，无本体归属）。且 README/AGENTS/CONTEXT/多个 skills/templates/任务 PRD 均把 `docs/adr/` 当作 ADR 权威写入位置。仅删文件不改引用会留下死链与失效的 ADR 写入流程。

## 假设与结果

- 假设：A 组 ADR 决策可承载进本体节点（已存在则追加「决策背景」段），B 组删除，`docs/adr/` 删除，并把全仓引用改写为"决策记录本体化"，可使事实单一、可机读、可演进且不自相矛盾。
- 结果：A 组 8 ADR 决策载入 7 个本体节点（pdca-task 承载 0002+0017）；B 组 24 子系统 ADR 删除；`docs/adr/` 目录删除；14 个引用文件改写；本体校验通过。

## 分析

- **AC-1** ✅ A 组 8 个 ADR（0001-0004/0017/0024/0030/0031）决策均载入本体节点（ontology-asset / pdca-task / pdca-evidence / pdca-continuous-improvement / task-record-identity / ontology-creation-gate / pdca-ontology-ready）的「决策背景」段，原文件删除（t0419-migration）
- **AC-2** ✅ B 组 24 个子系统 ADR 文件已删除（t0419-migration）
- **AC-3** ✅ `docs/adr/` 目录已删除（含 .gitkeep）（t0419-migration）
- **AC-4** ✅ 14 个文件引用改写为"决策记录本体化"：README.md、AGENTS.md、pdca/CONTEXT.md（术语表 ADR 定义 + dependencies 引用 ADR-0017）、flows/flow-plan/SKILL.md、skills/{grilling,domain-modeling-work,improve-codebase-architecture,tdd}、templates/to-spec/SPEC.md、docs/{project-architecture-design,ONTOLOGY_GUIDE}、ontology/README.md、ontology/concept/pdca-architecture-review-metrics.md、knowledge/.../rpc-conn-idle-reclaim.md；grep 确认 `scripts/SKILL/flows/docs/templates` 无 `docs/adr` 残留（t0419-reference-v2）
- **AC-5** ✅ `ontology-validate.py` 通过（退出码 0、无悬空引用、无环），`ontology_graph` islands=0，新节点合规（t0419-validate）
- **AC-6** ✅ 登记证据（t0419-migration / t0419-reference-v2 / t0419-validate）并写入收敛映射（t0419-convergence-v2）；`validate-convergence.py` 通过（valid:true，无 issues）（t0419-convergence-v2 / t0419-reference-v2）

## 失败原因

- 无（全部 AC 满足）

## 适用边界

- 历史 `records/`、`pdca/journal/`、`pdca/tasks/` 下任务 PRD 中的 `docs/adr` 引用属不可变记录溯源，按 AC-6 例外保留，未改动。
- ontology/concept 节点正文对 `docs/adr` 的历史性描述（如 ontology-asset 背景中"曾引用 ADR 机制"）保留为叙述，非活动引用。
- 本任务不迁移 B 组决策到其它项目仓库（仅删除本仓库副本）。

## 下一轮建议

- 后续不可逆非显然决策统一写入对应 `ontology/` 节点（加「决策背景」段），不再使用 ADR 文件；技能/模板已同步该约定。
- 若后续需查阅某已删子系统 ADR 的原始内容，可从其对应项目仓库或 records/ 历史记录中溯源。

## Verdict（建议，待用户确认固化）

- **outcome**: confirmed
- **reason**: 6 项 AC 全部满足；A 组决策已承载进本体、B 组与目录已删除、全仓引用改写为本体化且 grep 零残留、本体校验通过、证据与收敛映射齐备。
- **verdict_id**: verdict-t0419-confirmed
- **at**: 2026-08-30T09:57:30+08:00
- 此区块由用户 `check_confirmation` 确认后写入 `task.json` `meta.verdict`，AI 不代签。
