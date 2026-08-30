---
schema: pdca.asset/v1
id: T0420-0830-knowledge-adr-refs-cleanup
phase: check
source_ids: [t0420-reference-v2, t0420-validate, t0420-convergence-v3]
---

# T0420 结论：清理 knowledge/ 下对已删 ADR 的引用

## 上下文

T0419 全量删除 `docs/adr/`（含 ADR-0030/0022/0016/0007 等）后，`knowledge/` 下仍有 19 个文件引用已删 ADR：16 个重定向桩含"按 ADR-0030 物理归并"，3 个真实知识文件含 ADR-0016/0022/0007 的来源/溯源引用。为保持"决策记录本体化、无悬空 ADR 引用"的一致性，予以清理（不删文件、不改本体）。

## 假设与结果

- 假设：将桩文件的历史原因改为指向本体节点 `ontology-creation-gate` 决策背景、将真实文件的 ADR 溯源改为任务号/records，可消除悬空引用且不影响功能。
- 结果：19 个文件全部改写完成；`grep -rn "ADR-[0-9]" knowledge/` 归零；本体校验通过。

## 分析

- **AC-1** ✅ 16 个重定向桩"本文件已按 ADR-0030 物理归并至本体库"→"本文件已按 `ontology:concept/ontology-creation-gate` 决策背景物理归并至本体库"（t0420-reference-v2）
- **AC-2** ✅ `knowledge/linux-epoll-eventloop/rpc-conn-idle-reclaim.md` 移除 ADR-0016 引用，保留 records/ 溯源说明（t0420-reference-v2）
- **AC-3** ✅ `knowledge/lmdb/vl32-no-mmap-build-gate.md` 移除 "and ADR-0022"，保留 T0249 任务号溯源（t0420-reference-v2）
- **AC-4** ✅ `knowledge/ai-efficiency/skills-candidate-review.md` 移除 ADR-0007 引用（t0420-reference-v2）
- **AC-5** ✅ `grep knowledge/` 无 ADR 残留；`ontology-validate.py` 通过、islands=0（t0420-reference-v2 / t0420-validate）
- **AC-6** ✅ 登记 reference/validate/convergence 证据 + 收敛映射，`validate-convergence.py` 通过（valid:true）（t0420-reference-v2 / t0420-convergence-v3）

## 失败原因

- 无（全部 AC 满足）

## 适用边界

- 仅改动 `knowledge/` 文本，未删文件、未改本体节点；`scripts/SKILL/flows/docs/templates/ontology` 不在本任务范围（T0419 已处理）。
- `records/`、`pdca/journal/`、`pdca/tasks/` 下历史任务 PRD 中的 ADR 引用属不可变记录溯源，按约定保留。

## 下一轮建议

- 全仓 ADR 残留现已清零（活动文件仅含本体节点「决策背景」段的历史归属注记）。
- 后续不可逆非显然决策统一写入对应 `ontology/` 节点，不再使用 ADR 文件。

## Verdict（建议，待用户确认固化）

- **outcome**: confirmed
- **reason**: 6 项 AC 全部满足；knowledge/ 下 19 个已删 ADR 引用已全部改写/移除、grep 归零、本体校验通过、证据与收敛映射齐备。
- **verdict_id**: verdict-t0420-confirmed
- **at**: 2026-08-30T10:10:40+08:00
- 此区块由用户 `check_confirmation` 确认后写入 `task.json` `meta.verdict`，AI 不代签。
