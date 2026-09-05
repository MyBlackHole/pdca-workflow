---
schema: pdca.asset/v1
id: T0497-0906-bcachefs-kernel-round9
phase: check
source_ids: [node-core-btree-node-scan-rebuild, node-core-journal-pin-lifetime-flush, node-core-backpointer-dup-to-reflink, node-core-damage-ledger-inherit, node-core-util-sync-primitives, validate-output, convergence-map]
---

## 上下文
用户要求内核第九轮二轮复核。Plan 定全范围复核 + 新增至少 2 节点。Do 两片并行得 21 条遗漏机制（borderline 已弃、不足如实报告），新增 5 节点与互链方案经用户确认后执行。

## 假设与结果
- 假设 1：复核条目确为遗漏。结果：成立，每条带不重复理由；重复候选已剔除 9 条。
- 假设 2：5 节点互链单向无环。结果：成立，validate 全量通过。
- 假设 3：立项文件无误。结果：成立，一次验证通过。

## 分析
- **AC-1** ✅ 21 条复核机制，每条带不重复理由与代码位置（5 node 证据正文引用）
- **AC-2** ✅ 新增 5 个不重复 domain 节点且 frontmatter 合法（5 node 证据）
- **AC-3** ✅ 互链单向关联落实，validate 无环证明，未动历史节点（node 证据 + validate-output）
- **AC-4** ✅ validate 全量 0 issues，信号非泛化，引用无空悬（validate-output）

关键结论：新增 core-btree-node-scan-rebuild、core-journal-pin-lifetime-flush、core-backpointer-dup-to-reflink、core-damage-ledger-inherit、core-util-sync-primitives。
复核途径：validate 输出 OK；逐节点 Read 核对。

## 适用边界
- 本次未改动任何历史节点；优化=新节点互链。
- str_hash/ACL/读提升落选备选，机制留存在深挖记录中。

## 下一轮建议
- 内核已覆盖 43 节点；建议收官或转向用户态/信号治理。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，5新节点单向互链，validate 0 issues", "verdict_id": "vt0497-confirmed", "at": "2026-09-06T00:00:00+08:00"}
