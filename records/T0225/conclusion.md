---
schema: pdca.asset/v1
id: T0225
phase: check
source_ids: [research-report, ac-source-anchors]
---

## 上下文

调研 Percona XtraBackup 8.0.25（`goldendb-xtrabackup`，标准源码快照）支持哪些 MySQL 增量备份实现方案，并要求联网对照第三方/缺失方案。

## 假设与结果

| PRD 假设 | 结果 |
|---------|------|
| 存在「全表扫描比对页 LSN」增量主路径 | ✅ 成立，write_filt.cc:125-126 证实 |
| 支持 changed-page bitmap（依赖 Percona Server） | ✅ 成立，backup_mysql.cc:683-685/2179-2186 |
| 有 redo log archiving 机制 | ✅ 成立，redo_log.cc:639-736 |
| 增量 prepare 用 apply-log-only + delta 应用 | ✅ 成立，xtrabackup.cc/backup 链路 |
| `--rollback-only`/`--redo-lag` 为已实现支持项（PRD 原假设） | ❌ 修正：8.0.25-17 已移除（无符号） |
| 本项目支持官方 page tracking 增量 | ❌ 修正：8.0.25 无 `--page-tracking`（8.0.27 起） |

## 分析

- 9 项验收标准全部达成，`validate-convergence` 返回 valid:true。
- 发现较 PRD 更准确的边界：`--page-tracking`（8.0.25 缺失）、`--rollback-only`/`--redo-lag`（已移除）、8.0.30 移除 Percona changed-page 算法、8.4.0-3 并行 delta 合并。
- 支持矩阵清晰区分「已实现」「缺失」「互补」，第三方方案引用官方文档。

## 失败原因

（无 — 结论成立；PRD 内个别项在 Do 期经代码核验修正为更准确状态，不构成失败。）

## 适用边界

- 结论基于 8.0.25-17 源码静态分析 + 联网官方资料；未实际编译运行、未做性能基准。
- page tracking（官方）与 Percona changed-page 位图为两套不同机制，引用时勿混淆。
- 版本能力随版本演进（8.0.27/8.0.30/8.4）差异显著。

## 下一轮建议

- 如需使用官方 page tracking 增量，建议评估升级至 ≥8.0.27。
- 可按需在 Act 阶段把「XtraBackup 增量方案速览」正式登记为 knowledge。