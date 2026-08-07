---
schema: pdca.asset/v1
id: T0225
phase: check
source_ids: [research-report, ac-source-anchors]
---

## 上下文

调研 Percona XtraBackup 8.0.25（`goldendb-xtrabackup`，标准源码快照）支持哪些 MySQL 系列增量备份实现方案，并对照 MariaDB / Percona Server / 官方 page tracking 的版本能力边界。用户口径收敛为「**真增量 = 免全表扫描、只读变化页**（page tracking / bitmap）」，排除还原阶段（prepare）与备份一致性通用机制（redo 归档）。

## 假设与结果

| PRD 假设 | 结果 |
|---------|------|
| 存在「全表扫描比对页 LSN」物理增量主路径 | ✅ 成立，write_filt.cc:125-126 证实 |
| Changed-Page-Bitmap（依赖 Percona Server） | ✅ 成立，backup_mysql.cc:683-685/2179-2186；仅 Percona Server 置位 |
| MariaDB 真增量 | ✅ 成立（联网佐证）：仅 10.0/10.1 XtraDB 位图（CHANGED_PAGE_BITMAPS 插件），10.2+ 移除 |
| 官方 page tracking | ❌ 本项目缺失（引擎 8.0.17+，PXB 消费端 8.0.27+） |
| `--rollback-only`/`--redo-lag` 为已实现支持项（PRD 原假设） | ❌ 修正：8.0.25-17 已移除（无符号） |
| 增量 prepare / redo 归档 / history 续作 属增量方案 | ❌ 口径修正：prepare=还原阶段、redo 归档=通用一致性、history=LSN 起点选取，均不计入真增量 |

## 分析

- 9 项验收标准全部达成，`validate-convergence` 返回 valid:true（research-report-v12 / convergence-map-v12）。
- 版本矩阵：Percona Server 位图 5.5.27 引入；MySQL 官方 page tracking 引擎 8.0.17（Clone）、MEB 8.0.18 默认消费、PXB 8.0.27 `--page-tracking`；MariaDB 位图 10.0/10.1（FLUSH 10.1.6）后移除。
- 缺口断言全仓检索证实：`--page-tracking`、`--rollback-only`、`--redo-lag` 在本版本无符号。
- 代码证据附录 A1（全扫描）、A2（bitmap）均为源码主证；MariaDB/MEB/page-tracking 版本能力为联网佐证。

## 失败原因

（无 — 结论成立；PRD 内个别项在 Do 期经代码核验与用户口径澄清后修正为更准确状态，不构成失败。）

## 适用边界

- 结论基于 8.0.25-17 源码静态分析 + 联网官方资料；未实际编译运行、未做性能基准。
- page tracking（官方）与 Percona changed-page 位图为两套不同机制，引用时勿混淆。
- 版本能力随版本演进（8.0.27/8.0.30/8.4）差异显著。
- MariaDB / MEB / PS 版本起点为联网佐证，如需工程级结论建议在对应发行说明上独立复核。

## 下一轮建议

- 如需使用官方 page tracking 增量，建议评估升级至 ≥8.0.27。
- 真增量选型：Percona Server（bitmap，立即可用）或 MySQL 8.0.27+（官方 page-tracking）。
