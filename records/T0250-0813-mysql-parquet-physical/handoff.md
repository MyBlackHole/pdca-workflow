## 当前状态
T0250（MySQL/PG 物理直读→Parquet）已 verdict=confirmed，Act 阶段收尾：disposition=projected 已写入、知识沉淀完成（knowledge/manifest.jsonl 登记 + 源码副本）。归档进行中。

## 未完成事项
- 无（归档 mv 由 flow-act Ac8 完成；后续如有旧 BLOB 页 type22 / PG9.x pg_clog 需求，可在 mysql_lob_legacy_pre8013.c / pg_clog_legacy_pg9.c 中实现）

## 已知约束
- 旧 BLOB 页（8.0.13 前）与 PG9.x 及更早 CLOG 仅占位未实现（恒 -1，显式失败不静默错读）
- 100M 吞吐口径以 3 轮 json 中位 68.3s/1.46M 行/s 为准（快 4.2×）
- 测试数据（.ibd/parquet/100M json）不得进入 pdca 仓库

## 推荐的下一步
- 结束本任务；新需求（如 type22/旧 CLOG）走 Plan→Do→Check→Act 新任务

## 关键上下文文件列表
- knowledge/data-formats/mysql-innodb-physical-read-notes.md（含版本差异矩阵）
- knowledge/data-formats/t0250-mysql-parquet-physical/（源码副本，版本文件名标注）
- records/T0250-0813-mysql-parquet-physical/conclusion.md（verdict confirmed）
- 源项目 src/mysql/mysql_versions.h / src/pg/pg_versions.h（版本特性矩阵）

## suggested skills
- chinese-environment（全中文项目）
- code-comments（源码中文注释）
- testing-strategy（解析验证/档位样本量）
