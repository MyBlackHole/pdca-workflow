---
schema: pdca.asset/v1
id: T2072-0909-six-scenario-research-first
phase: check
source_ids: [research-report, convergence-map]
---

## 上下文
任务 T2072 按口径A核验六场景是否严格先调研后操作。Do已产 research-report.md（4 mermaid/14 Source）并登记 evidence，convergence valid:true。

## 假设与结果
假设：六场景Do准入均强制 ontology-ready，复用即算先调研。结果成立：六场景全部命中准入，仅自举豁免。

## 分析
- **AC-1** ✅ 六场景前置门禁已逐项核验（research-report）
- **AC-2** ✅ 每结论附可复核验证途径（research-report）
- **AC-3** ✅ research-report已登记为证据（convergence-map）

逐场景判定：
- development ✅ Do准入ontology-ready（scripts/ontology_gate.py:37-43）+消费fragment+Act回写（scripts/pdca_core.py:447-451）。验证：python3 scripts/ontology_reason.py admission --phase do
- bugfix ✅ 同上，路径B先复现回归测试（ontology/process/flow-do.md:59-67）。验证：查 flow-do.md:59-67
- research ✅ 本身生产本体，多图门禁（ontology/domain/pdca/skill-research.md:73-84）。验证：grep -c mermaid research-report.md
- documentation ✅ Diataxis选型+图Source门禁同research（ontology/process/flow-do.md:76-80）。验证：查 flow-do.md:76-80
- design ✅ design-it-twice双方案+grilling复核（ontology/process/flow-do.md:82-86）。验证：查 flow-do.md:82-86
- review ✅ 双轴并行+grilling复核（ontology/process/flow-do.md:88-92）。验证：查 flow-do.md:88-92

## 适用边界
仅适用于本仓库当前元本体含 pdca-gate-do→ontology-ready 的版本；自举任务豁免；fragment可复用不必每次新建research票。

## 下一轮建议
保持门禁；新增场景先声明准入；定期跑 scenario-boundary-check 防 research/development 错配。

## 本体沉淀
判定为 ontology：六场景先本体后操作矩阵具跨任务复用价值，拟在 Act 新建 ontology:concept/scenario-research-first-gate。来源 record T2072-0909-six-scenario-research-first。

## 证据索引
- research-report / convergence-map

**verdict**: confirmed
- outcome: confirmed
- reason: 六场景逐项核验通过，收敛valid:true
- verdict_id: v2072-confirmed
- at: 2026-09-09T10:22:04+08:00
