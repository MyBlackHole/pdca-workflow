---
schema: pdca.asset/v1
id: T0543-0906-ec-algorithm
phase: check
source_ids: [node-core-ec-rs-math, node-core-ec-stripe-geometry, node-core-ec-stripe-alloc, validate-output, ac3-verify, convergence-map-v2]
---

## 上下文
用户指出缺少 EC 算法本身本体，确认 RS 数学/几何布局/分配 widen 三层全建。

## 假设与结果
- 假设 1：三层可独立成篇。结果：成立，数学/几何/分配各有源码锚点。
- 假设 2：RS 数学不超范围。结果：成立，只讲 P/Q 子集，不展开通用编码理论。

## 分析
- **AC-1** ✅ 三节点详实：RS 两档生成四分支恢复、几何变长三段、质心逐块重算（3 node 证据）
- **AC-2** ✅ 三查 0 issues，validate 全绿（node 证据 + validate-output）
- **AC-3** ✅ 证据登记完成，Check 门禁通过（ac3-verify）

关键结论：新增 core-ec-rs-math、core-ec-stripe-geometry、core-ec-stripe-alloc。
复核途径：Read 核对三层与源码对应。

## 本体沉淀

决策：`ontology:ontology:domain/core-ec-rs-math`、`ontology:domain/core-ec-stripe-geometry`、`ontology:domain/core-ec-stripe-alloc`。

理由：EC 算法本身三层属可复用知识。来源 record `T0543-0906-ec-algorithm`。

## 适用边界
- RS 数学只覆盖 P/Q 子集；几何以 format.h 为准；分配以现树 create.c 为准。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，算法三层节点", "verdict_id": "vt0543-confirmed", "at": "2026-09-06T00:00:00+08:00"}
