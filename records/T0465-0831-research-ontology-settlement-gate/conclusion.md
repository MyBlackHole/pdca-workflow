---
schema: pdca.asset/v1
id: T0465-0831-research-ontology-settlement-gate
phase: check
source_ids: [evidence-summary, skill-research-patch, flow-act-patch, settlement-check, validation-report, convergence-map]
---

# 结论：T0465 建立 research 场景的本体沉淀门禁，避免知识仅留 records

## 上下文

T0464 复盘发现 research 场景的 `ontology-ready` 仅校验 `ontology_fragment` 存在（根目录即过），`skill-research` 合约以“报告+证据”完成，未在 Act 强制“ontology vs records-only”显式决策，导致高复用知识（12维+L1-L4+B1-B4）仅留 `records`。用户要求“同时创建新任务处理这个问题，避免下次再次发生”。本任务即为该改进。

已追补：`ontology:domain/tool-production-readiness`（`ontology/domain/tool-production-readiness.md:1`）作为正例，已通过 `ontology-validate` 与 `ontology_graph`。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| research 本体沉淀可被流程显式约束且漏本体化可拦截 | 成立：新增 `check-research-ontology-settlement.py`，漏 `##本体沉淀` 或 `disposition` 无显式词即拦截 | settlement-check, evidence-summary |
| skill-research 与 flow-act 可补强并与本体校验衔接 | 成立：`skill-research` 新增本体沉淀决策四步，`flow-act` 三处挂接新门禁 | skill-research-patch, flow-act-patch, validation-report |
| 提供可回归校验，T0464类高复用研究不再仅留 records | 成立：T0464 正例通过，新负例可拦截 | settlement-check, validation-report |

## 分析

- **AC-1** ✅ 在 `skill-research` 新增 `## 本体沉淀决策（Act 门禁）`（分流判定3条+决策记录+本体化执行+校验）与 `flow-act` 三处补强，且与 `pdca-ontology-ready` 衔接（skill-research-patch, flow-act-patch）
- **AC-2** ✅ 提供 `scripts/check-research-ontology-settlement.py`，校验 `conclusion.md##本体沉淀` 显式含 `ontology:`/`records-only` 且 `meta.disposition.reason` 含显式词，漏决策即 `RESEARCH_SETTLEMENT_MISSING`（settlement-check, evidence-summary）
- **AC-3** ✅ 回归验证：T0464 补本体后 `OK: research settlement decision present for T0464`（exit 0）；构造漏 `##本体沉淀` 负例被拦截 `RESEARCH_SETTLEMENT_MISSING`（exit 1）；`records-only` 显式正例通过（settlement-check, validation-report）
- **AC-4** ✅ `ontology-validate OK`，`ontology_graph 350 nodes / 759 edges / 0 islands`，`SKILLS-INDEX` 已重生成 asset_count 48（validation-report）

> 复核命令：
> - `grep "本体沉淀决策" ontology/domain/skill-research.md`
> - `grep "check-research-ontology-settlement" ontology/process/flow-act.md`
> - `python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/archive/2026-08/0831-prod-tool-dev-requirements-research` # 正例
> - `python3 scripts/ontology-validate.py --ontology-dir ontology && python3 scripts/ontology_graph.py | grep islands`

## 本体沉淀

- 决策：`ontology` — 本任务产出为流程改进，补强 `skill-research` 与 `flow-act` 两个 Knowledge 资产，属可复用方法论
- 关联：`ontology:domain/skill-research`、`ontology:process/flow-act`、`ontology:domain/tool-production-readiness`（正例）、`ontology:concept/pdca-ontology-ready`
- 校验：`ontology-validate OK`，`ontology_graph 0 islands`

## 适用边界

- 分流阈值按“是否产出可复用清单/模型/模式/阈值”判定，一次性事实收集可 `records-only` 但须在 `conclusion` 与 `disposition` 显式声明理由
- 本门禁仅作用于 `scenario_type=research` 且 `phase in (act, archive)`，非 research 或未到 act 时 `check-research-ontology-settlement.py` 跳过

## 下一轮建议

1. 在后续 research 任务的 Act 模板中预置 `## 本体沉淀` 小节，避免漏写
2. 考虑将 `check-research-ontology-settlement.py` 接入 `archive` 门禁的自动化校验（当前为独立脚本，需手工运行）
3. 若出现新的高复用 research，可按本门禁直接产出 `ontology/domain` 或 `ontology/pattern` 节点

## Verdict

- outcome: confirmed
- reason: 4 项 AC 全部满足，3 项 convergence 均有 evidence 支撑且经 validate-convergence 通过，门禁可拦截漏本体化且 T0464 正例已追补通过
- verdict_id: v0465-confirmed-0831
- at: 2026-08-31T17:58:30+08:00
