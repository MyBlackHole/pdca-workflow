---
schema: pdca.asset/v1
id: T2179-0911-independent-pdca-ticket-gate-projection
phase: check
source_ids: [t2179-gate-runtime-c1, t2179-ticket-tests-c1, t2179-research-tests-c1, t2179-verification-report-c1, convergence-map-c1]
---

# T2179 独立任务门禁投射结论

## 上下文

T2178 完成 Plan 后被旧 `TICKETS_MISSING` 门禁阻断。T2179 作为独立本体自举投射任务，只负责把 `ontology:concept/pdca-task` 的任务独立性落实到 Plan→Do 准入，不承担旧场景本体清理或 Agent runtime 全量投射。

## 假设与结果

假设成立：删除任务拆解强制准入及跨任务研究状态遍历后，parentless、无 children 的任务可以独立进入 Do，同时保留 final confirmation、Grill、PRD、本体就绪和研究报告质量等其他门禁。

首次实现只删除了 `TICKETS_MISSING`，仍通过 `_research_first_ok` 遍历关联任务状态，被主协调器的 `ontology_conformance_verification` 判定不符合 AC-2。修正后，研究准入只读取当前任务自身持久化的 `research-report.md`，跨任务生命周期耦合已移除。

## 分析

- **AC-1** ✅ 无 parent、无 children 的独立任务在其他 Plan 条件满足时不再产生 `TICKETS_MISSING`。（t2179-gate-runtime-c1, t2179-ticket-tests-c1, t2179-verification-report-c1）
- **AC-2** ✅ Plan 准入不再读取 parent、children、dependencies 或关联任务 archive 状态；研究门禁仅读取当前任务产物。（t2179-gate-runtime-c1, t2179-research-tests-c1, t2179-verification-report-c1）
- **AC-3** ✅ `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification` 三种职责均覆盖 parentless、children=[] 的独立准入回归。（t2179-ticket-tests-c1, t2179-verification-report-c1）
- **AC-4** ✅ 直接测试 6 passed/3 subtests，相关 Plan 门禁回归 10 passed/3 subtests；final confirmation、Grill、研究、本体就绪及合法转换测试均通过。（t2179-ticket-tests-c1, t2179-research-tests-c1, t2179-verification-report-c1）
- **AC-5** ✅ 目标实现及测试中不存在 `TICKETS_MISSING`、旧 child-ticket 消息、任务索引遍历或 parent-leaf 豁免控制分支。（t2179-gate-runtime-c1, t2179-ticket-tests-c1, t2179-research-tests-c1, t2179-verification-report-c1）

## 适用边界

- 本结论只确认独立任务与 Plan→Do 门禁之间的最小投射。
- 扩展诊断仍有旧 fixture、doctor 和设计词汇测试失败；它们不执行本任务修改的 ticket/cross-task 准入分支，已如实保存在验证报告中，不计为通过。
- `research_required` 的 role 默认逻辑、旧六场景本体、`agent.spawn`、协调挂起及恢复机制仍需后续独立 PDCA 处理。

## 下一轮建议

完成 T2179 后重新执行 T2178 的 Plan→Do 门禁；T2178 只清理核心权威本体中的旧场景控制语义。

## 判定

- outcome: confirmed
- reason: AC-1 至 AC-5 均由当前有效证据覆盖，首次跨任务遍历缺口已修正，直接测试和相关 Plan 门禁回归全部通过。
- verdict_id: V-T2179-20260911
- at: 2026-09-11T15:43:05+08:00

## 本体沉淀

- disposition: ontology
- 投射来源：`ontology:concept/pdca-task`。
- 实现落点：Plan→Do 门禁不再以 parent、children、dependencies 或关联任务状态控制当前任务生命周期；研究准入只读取当前任务自身持久化产物。
- 复用理由：该约束适用于三个专业职责下的所有独立 PDCA，是流程 runtime 的通用投射规则。
