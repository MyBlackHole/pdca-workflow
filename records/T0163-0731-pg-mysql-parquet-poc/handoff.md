# Handoff — T0163 PG/MySQL 导出 Parquet POC

## 当前状态
- 任务已 verdict=confirmed（2026-07-31），正在执行 Act 收尾（Ac7 提交 / Ac8 归档）。
- 六路径 1M 行三轮中位数 + 1 亿行两路径实测全部完成，证据 18 条 manifest digest 一致（`records/T0163-0731-pg-mysql-parquet-poc/evidence/manifest.jsonl`）。
- 知识已沉淀 2 篇（`knowledge/data-formats/pg-to-parquet-path-benchmark.md`、`pg-heap-physical-read-notes.md`），journal 已追加，disposition=projected 已写入 task.json。

## 未完成事项
- 无阻塞项。归档（advance-phase → archive + 任务目录迁移）未执行。

## 已知约束
- 结论基于 PG 18.4 单容器本地环境；100M 仅实测 D2 与 C++ 两路径（单次，RSS 为硬指标）；D2 读侧 100M 数值为 1M 线性外推。
- MySQL 实测按用户决策取消，`mysqlsh` 缺口已登记。
- 物理路径需 CHECKPOINT 保证一致；TOAST 列未覆盖；PG 12~16 兼容性未验证。
- 遗留环境噪声：后台 opencode×2、容器内挂起 apt-get；/home 磁盘剩 ~31G（100M 测试需规避 /tmp tmpfs 1.5G）。

## 推荐的下一步
1. 归档本任务（Ac8）；按需新建任务：D2 10 亿+ 行分片策略、TOAST 列物理直读、PG 12~16 兼容性、MySQL 同口径实测。
2. 工程化落地参考 `knowledge/data-formats/pg-heap-physical-read-notes.md`（含 3 个已修复 bug 教训），pgbin 源码在任务目录与 evidence（批处理版）。

## 关键上下文文件列表
- records/T0163-0731-pg-mysql-parquet-poc/conclusion.md（结论+source_ids）
- records/T0163-0731-pg-mysql-parquet-poc/evidence/research-report.md（§8 含不同数据量对照表）
- records/T0163-0731-pg-mysql-parquet-poc/evidence/pg_cpp_100m_metrics.json（1 亿行指标）
- pdca/tasks/0731-pg-mysql-parquet-poc/{pg_heap_reader.c, main.cpp, stub_pg.c, cpp_path_repro.md}（批处理最终版）
- knowledge/data-formats/pg-to-parquet-path-benchmark.md、pg-heap-physical-read-notes.md

## suggested skills
- 后续工程化任务：`build-config`（编译链）、`code-review-checklist`、`testing-strategy`
