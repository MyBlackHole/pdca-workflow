---
schema: pdca.asset/v1
id: T0421-0830-active-adr-refs-cleanup
phase: check
source_ids: [t0421-reference, t0421-validate, t0421-convergence]
---

# T0421 结论：清理活动机制文件中的已删 ADR 悬空引用

## 上下文

全仓最终扫描发现 3 个活动机制文件仍含不带路径前缀的已删 ADR 引用（此前 T0419/T0420 按 `docs/adr` 前缀 grep 漏掉）：`pdca/CONTEXT.md` 的 ADR-0018/0029、`scripts/ontology-validate.py` 的 ADR-0030 注释、`pdca/skill-content-baseline.json` 的 ADR-0007（约 25 处）。这些均指向已在 T0419 中删除的 ADR 文件，属悬空引用。

## 假设与结果

- 假设：将 CONTEXT.md 溯源改为历史注记、将校验器注释指向本体节点、将基线 reason 去 ADR，可消除悬空引用且不影响功能。
- 结果：3 个文件全部改写完毕；全仓活动文件（排除 records/journal/tasks/health-audit）grep 仅剩本体节点「原/formerly ADR-XXXX」历史归属注记（有意保留），无 `docs/adr` 前缀引用、无指向已删 ADR 文件的链接；本体校验通过。

## 分析

- **AC-1** ✅ `pdca/CONTEXT.md` 的 ADR-0018/0029 引用改写为"历史决策，已随 docs/adr/ 退役删除"（t0421-reference）
- **AC-2** ✅ `scripts/ontology-validate.py` 3 处 ADR-0030 注释改为指向 `ontology:concept/ontology-creation-gate` 决策背景（t0421-reference）
- **AC-3** ✅ `pdca/skill-content-baseline.json` 25 处 "Initial ADR-0007 baseline" → "Initial baseline"（t0421-reference）
- **AC-4** ✅ 全仓活动文件 grep 无 `docs/adr` 前缀及已删 ADR 悬空引用；仅保留本体节点「原/formerly ADR-XXXX」历史归属注记（t0421-reference）
- **AC-5** ✅ `ontology-validate.py` 通过、islands=0；登记 reference/validate/convergence 证据 + 收敛映射，`validate-convergence.py` valid:true（t0421-reference / t0421-validate / t0421-convergence）

## 失败原因

- 无（全部 AC 满足）

## 适用边界

- 仅改动 3 个活动文件文本/注释，未删文件、未改本体、未改脚本行为。
- 本体节点 / `docs/ONTOLOGY_GUIDE.md` / `ontology/README.md` 中的"原/formerly ADR-XXXX"为有意历史归属注记（新约定），不在清理范围。
- `records/`、`pdca/journal/`、`pdca/tasks/` 下历史任务 PRD 的 ADR 引用属不可变记录溯源，保留。

## 下一轮建议

- 全仓 ADR 悬空引用现已清零；后续不可逆非显然决策统一写入对应 `ontology/` 节点（加「决策背景」段），不再使用 ADR 文件。
- 建议在 `pdca-doctor` 或 CI 中加入"禁止新增 `ADR-[0-9]` 字面引用（本体节点「原 ADR-XXXX」注记除外）"的静态检查，防止回流。

## Verdict（建议，待用户确认固化）

- **outcome**: confirmed
- **reason**: 5 项 AC 全部满足；3 个活动文件的已删 ADR 悬空引用已全部改写/移除、全仓活动文件 grep 仅剩有意历史注记、本体校验通过、证据与收敛映射齐备。
- **verdict_id**: verdict-t0421-confirmed
- **at**: 2026-08-30T10:16:40+08:00
- 此区块由用户 `check_confirmation` 确认后写入 `task.json` `meta.verdict`，AI 不代签。
