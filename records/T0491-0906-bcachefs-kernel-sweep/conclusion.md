---
schema: pdca.asset/v1
id: T0491-0906-bcachefs-kernel-sweep
phase: check
source_ids: [node-core-btree-transaction-memory-io, node-core-bkey-packed-encoding, node-core-superblock-readback-validation, node-core-compress-retry-verify, node-core-pagecache-buffered-direct-io, validate-output, convergence-map]
---

## 上下文
用户要求内核范围继续分析并优化本体。Plan 定全范围遗漏扫描 + 新增至少 3 节点 + 优化分析后定。Do 三片并行得 35 条遗漏机制，新增 5 节点清单与新节点互链优化经用户确认后执行。

## 假设与结果
- 假设 1：三片深挖均为前两轮遗漏。结果：成立，prompt 明确排除已建 15 节点主题，返回 35 条新机制。
- 假设 2：新节点互链单向无环。结果：成立，validate 全量通过。
- 假设 3：真实时间戳合规。结果：成立，transition 一次通过（T0490 教训已落实）。

## 分析
- **AC-1** ✅ 三片 35 条遗漏机制，每条带文件+函数名（5 node 证据正文引用）
- **AC-2** ✅ 新增 5 个不重复 domain 节点且 frontmatter 合法（5 node 证据）
- **AC-3** ✅ 优化=新节点互链单向关联，validate 无环证明，无历史节点改动（node 证据 + validate-output）
- **AC-4** ✅ validate 全量 0 issues，信号非泛化，引用无空悬（validate-output）

关键结论：新增 core-btree-transaction-memory-io、core-bkey-packed-encoding、core-superblock-readback-validation、core-compress-retry-verify、core-pagecache-buffered-direct-io。
复核途径：validate 输出 OK；逐节点 Read 核对。

## 适用边界
- B 片 journal/sb 部分条目是对 T0488 概览的深化而非全新发现，已在节点正文中收敛为互补视角。
- C 片 util 小件罗列较广，未全部建节点（规模控制），机制留存在深挖记录中。
- 本次未改动任何历史节点。

## 下一轮建议
- EC 修复状态机、journal 空间记账、快照删除执行可作为后续新增候选。
- 老 core-* 节点 testable_signal 泛化宜单独立项批量治理。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，5新节点单向互链，validate 0 issues", "verdict_id": "vt0491-confirmed", "at": "2026-09-06T00:00:00+08:00"}
