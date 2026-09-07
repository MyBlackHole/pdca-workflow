---
schema: pdca.asset/v1
id: T0545-0906-conformance-audit
phase: check
source_ids: [audit-script, audit-report, fix-diff, convergence-map]
---

## 上下文
用户要求全量审计本体符合度。102 节点自动化审计 + 人工核实修复。

## 假设与结果
- 假设 1：脚本误报可控。结果：初版 44 警告多为搜索范围不足，经两轮修正（全仓库索引、rs 扩展、哈希跳过）降至 6 真问题。
- 假设 2：剩余警告可人工判定。结果：成立，6 个全为真问题（符号不存在或误用），已逐个修复。
- 假设 3：脚本自身 bug 可发现。结果：成立，BRE 不支持界定符 bug 在验证中暴露并修复。

## 分析
- **AC-1** ✅ 审计脚本实现，跑全 102 节点：0 确错，警告 44→6→0（audit-script）
- **AC-2** ✅ 审计报告：初版误报多，最终 6 真问题（误用符号/杜撰缩写/过期引用）（audit-report）
- **AC-3** ✅ 5 节点 6 处修复，回归全绿（fix-diff）

关键结论：存量符合度 96/102 直接通过，6 处符号误用已修复；脚本两处自身 bug 已修。
复核途径：重跑审计脚本应 0/0；git diff 查 5 节点修复。

## 本体沉淀

决策：`ontology:scripts/audit-ontology-conformance.py`（新检查脚本，支撑以后规避）。

理由：审计脚本本身即规避机制的执行载体。来源 record `T0545-0906-conformance-audit`。

## 适用边界
- 审计覆盖符号存在性，未覆盖语义正确性（需人工抽查）。
- 行号漂移未纳入本次（另行处理）。

## 下一轮建议
- 以后规避机制：新建本体引用必须跑审计脚本；行号引用改符号引用。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，102节点清零", "verdict_id": "vt0545-confirmed", "at": "2026-09-06T00:00:00+08:00"}
