---
schema: pdca.asset/v1
id: T0496-0906-bcachefs-kernel-round8
phase: check
source_ids: [node-core-journal-write-assembly, node-core-btree-commit-batch-filter, node-core-alloc-trigger-discard-duplex, node-core-nocow-logged-op-crashsafe, node-core-scrub-deferred-repair, node-core-util-containers-varint-fifo, validate-output, convergence-map]
---

## 上下文
用户要求内核第八轮全扫复核。Plan 定全范围复核 + 新增至少 2 节点。Do 两片并行得 21 条遗漏机制（均带不重复论证），新增 6 节点与互链方案经用户确认后执行；scrub 文件名误写事故已修正。

## 假设与结果
- 假设 1：复核条目确为遗漏。结果：成立，每条带不重复理由，子代理如实报告文件缺失与不足。
- 假设 2：6 节点互链单向无环。结果：成立，validate 全量通过。
- 假设 3：文件名事故无残留。结果：成立，误文件已删，正确文件一次验证通过。

## 分析
- **AC-1** ✅ 21 条复核机制，每条带不重复理由与代码位置（6 node 证据正文引用）
- **AC-2** ✅ 新增 6 个不重复 domain 节点且 frontmatter 合法（6 node 证据）
- **AC-3** ✅ 互链单向关联落实，validate 无环证明，未动历史节点（node 证据 + validate-output）
- **AC-4** ✅ validate 全量 0 issues，信号非泛化，引用无空悬（validate-output）

关键结论：新增 core-journal-write-assembly、core-btree-commit-batch-filter、core-alloc-trigger-discard-duplex、core-nocow-logged-op-crashsafe、core-scrub-deferred-repair、core-util-containers-varint-fifo。
复核途径：validate 输出 OK；逐节点 Read 核对。

## 适用边界
- 本次未改动任何历史节点；优化=新节点互链。
- 复核依赖子代理不重复论证，主会话抽查置信。

## 下一轮建议
- 内核已覆盖 38 节点；缝隙基本扫尽，建议收官或转向用户态/信号治理。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，6新节点单向互链，validate 0 issues", "verdict_id": "vt0496-confirmed", "at": "2026-09-06T00:00:00+08:00"}
