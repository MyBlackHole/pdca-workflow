---
schema: pdca.asset/v1
id: T2112-0910-line-ontology-design
phase: check
source_ids: [coverage-design, convergence-map]
---

## 上下文
T2112应用户纠偏由行级转向覆盖本质。Do已产双方案design.md并登记，收敛valid:true。

## 假设与结果
假设覆盖可判定且具名制可行。结果成立：推荐A声明覆盖，B降级补充。

## 分析
- **AC-1** ✅ 覆盖口径已对齐（coverage-design，round2转向）
- **AC-2** ✅ 双方案对比已产出（coverage-design）
- **AC-3** ✅ design已登记（convergence-map）

附带发现：`flow-do`写`--kind design`但代码允许集无`design`，本次以`document`登记，已如实记录为文档代码口径差。

## 适用边界
设计结论；实施（声明清单生成与判定门禁）另起development。

## 下一轮建议
实施覆盖门禁；补`evidence-design`子类型或修正flow-do写法二选一。

## 本体沉淀
判定为 ontology：拟在Act新建 ontology:concept/scope-coverage-gate。来源 record T2112-0910-line-ontology-design。

## 证据索引
- coverage-design / convergence-map

**verdict**: confirmed
- outcome: confirmed
- reason: 转向对齐，双方案完备，口径差已记录
- verdict_id: v2112-confirmed
- at: 2026-09-09T16:20:15+08:00
