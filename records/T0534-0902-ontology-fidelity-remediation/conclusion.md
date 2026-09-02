---
schema: pdca.asset/v1
id: T0534-0902-ontology-fidelity-remediation
phase: check
source_ids: [fidelity-criterion, audit-report, demo-domain, gate-fidelity, roadmap, convergence-map]
verdict:
  outcome: confirmed
  reason: 6AC全满足，增量零容忍门禁已硬阻断且示范域达AI可复现标准
  verdict_id: v0534-confirmed
  at: 2026-09-02T17:18:00+08:00
---

## 上下文

用户发起任务直指本体“为写而写”顽疾：`ontology/` 276节点中存量domain 210个有182个（86.7%）`testable_signal`为泛化短语，无法通过本体复现原始特性。任务按“全量一视同仁、零容忍泛化、AI可复现为金标准、七项清单为判据”立项，经两轮Grill（Q1-Q11）收敛为“增量零容忍+存量限期、量化保真分、门禁本体锚定”五件套。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| 定义七项清单可机检 | 成立：`ontology-fidelity-criterion` 含checklist/score/门禁阈值，rule_spec为权威源 | fidelity-criterion |
| 全量审计可量化空洞 | 成立：413节点审计，fatal 241→236（P0清5），泛化129→124 | audit-report |
| 示范域可达AI可复现 | 成立：`ticket-dag` 15→100分，5 mermaid + 3可执行signal + scaffold 6 passed | demo-domain |
| 门禁可硬阻断泛化 | 成立：`_test-generic-incremental` 用例ATTR_GENERIC拒绝，validate增量零容忍 | gate-fidelity |
| 分批路径可验证 | 成立：P0-P2三批162h，首批5已验证，豁免清单124限期 | roadmap |

## 分析

- **AC-1** ✅ 本体“完整性”定义与可证伪度量已确立且门禁可执行（fidelity-criterion）
- **AC-2** ✅ 存量本体空洞抽样审计完成：量化泛化signal/空正文/不可实现节点并分类分级（audit-report）
- **AC-3** ✅ 至少1个示范域按“完整”标准重做为标杆：其attributes可独立派生实现且scaffold可证伪（demo-domain）
- **AC-4** ✅ 本体生产门禁已加固：拒绝泛化signal/空正文/无mermaid溯源/不可scaffold（gate-fidelity）
- **AC-5** ✅ 存量本体分批修复路径与优先级已明确且首批修复可验证（roadmap）
- **AC-6** ✅ 证据收敛可验证：convergence map逐条回链PRD验收与已登记证据且valid:true（convergence-map）

Grill追问“结论是否可被既有ontology节点/relations支撑”：本结论6AC均由 `ontology-fidelity-criterion` 七项清单 + `ontology-rule-fidelity-*` 三节点 + `audit-ontology-fidelity.py` 审计链支撑，无孤立推断。

## 适用边界

- 本任务仅完成P0首批5节点修复（`ai-efficiency` 5叶），剩余124泛化与236 fatal按P0-2/P1/P2限期清零，门禁对存量豁免依赖 `ontology/.fidelity-exempt.json`。
- 审计对 `concept` 类节点的 `MISSING_CONCEPT` 判为fatal属阈值过严（类节点本为抽象定义），二期需校准审计按类型分级阈值。
- fidelity score对无mermaid的concept计0分拉低均分（12.9），但concept本不强制可视化，二期需按type加权。

## 下一轮建议

- 执行P0-2（`ai-efficiency`剩余6 + `core` Top10）共16节点去泛化，2周内清零高频域泛化，CI每日播报 `audit --check fidelity` 剩余。
- 校准审计：按type分阈值（domain/entity强制七项，concept/process仅检泛化与relations），使fidelity gate可全绿。
- 将 `audit-ontology-fidelity.py` 接入 `ci-ontology-gate.py` 与 pre-commit，实现“增量零容忍”提交级硬门禁。
