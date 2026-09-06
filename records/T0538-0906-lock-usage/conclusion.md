---
schema: pdca.asset/v1
id: T0538-0906-lock-usage
phase: check
source_ids: [node-six-usage, validate-output, ac3-verify, convergence-map-v2]
---

## 上下文
锁教学收官，用户下令生产锁使用本体节点。

## 假设与结果
- 假设 1：调用方规范可独立成篇。结果：成立，四规范不重复锁机制。
- 假设 2：三查一次通过。结果：初版缺机制节与编号条目，补后通过。

## 分析
- **AC-1** ✅ 四规范详实，每条有代码依据（node-six-usage）
- **AC-2** ✅ 三查初报 2 缺口已补，validate 全绿（node-six-usage + validate-output）
- **AC-3** ✅ 证据登记完成，Check 门禁通过（ac3-verify）

关键结论：新增 ontology:domain/core-six-usage-discipline。
复核途径：Read 核对四规范与源码对应。

## 本体沉淀

决策：`ontology:ontology:domain/core-six-usage-discipline`。

理由：调用方规范属可复用知识，与锁机制节点互补。来源 record `T0538-0906-lock-usage`。

## 适用边界
- 只讲调用方规范，不讲锁机制本身。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，调用方四规范节点", "verdict_id": "vt0538-confirmed", "at": "2026-09-06T00:00:00+08:00"}
