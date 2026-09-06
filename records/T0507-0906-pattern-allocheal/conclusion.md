---
schema: pdca.asset/v1
id: T0507-0906-pattern-allocheal
phase: check
source_ids: [pat-weighted-fair-allocation, pat-graded-selfhealing-schedule, pat-unified-relocation-engine, validate-output, convergence-map]
---

## 上下文
20 轮规划第 6 轮。从分配器与自愈 domain 节点提炼 pattern。

## 假设与结果
- 假设 1：pattern 与源 domain 不重复。结果：成立，体裁区分。
- 假设 2：pattern 门禁合规。结果：成立，validate 全量通过。

## 分析
- **AC-1** ✅ 每个pattern有源节点与代码依据（3 pattern 证据）
- **AC-2** ✅ 新增 3 个不重复 pattern 节点且 frontmatter 合法（3 pattern 证据）
- **AC-3** ✅ 关联单向无环，未动历史节点（pattern 证据 + validate-output）
- **AC-4** ✅ validate 全量 0 issues，信号非泛化，引用无空悬（validate-output）

关键结论：新增 ontology:pattern/weighted-fair-allocation、graded-selfhealing-schedule、unified-relocation-engine。
复核途径：validate 输出 OK；逐节点 Read 核对。

## 适用边界
- pattern 体裁为问题方案后果，不复述机制细节。
- 本次未改动任何历史节点。

## 下一轮建议
- 按 20 轮规划进入第 7 轮：原则节点提炼。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，3 pattern节点，validate 0 issues", "verdict_id": "vt0507-confirmed", "at": "2026-09-06T00:00:00+08:00"}
