# PostgreSQL DuckDB 转换 POC 报告

## 调研目标

用 DuckDB 补测两条路径，对照 pandas/psycopg2 路径：
1. D1: DuckDB 读既有 COPY CSV 转 Parquet（转换引擎替换，对照 pandas 转换层）。
2. D2: DuckDB postgres_scanner 直读 PG 表转 Parquet（端到端直转，对照 psycopg2 直转）。

## 方法

- DuckDB 1.5.5，COMPRESSION ZSTD，数据源为既有 poc_orders 表（1000000 行）。
- D1 输入: `poc-output/pg/pg_orders.csv`（112.7 MB，COPY CSV HEADER 产物）。
- D2 输入: `postgres_scan_pushdown('host=127.0.0.1 port=55432 dbname=poc user=postgres password=postgres', 'public', 'poc_orders')`。

## 发现

- D1（CSV→Parquet）耗时: 1.235s，吞吐 809831.68 rows/s
- D1 Parquet 大小: 26021511 bytes
- D2（PG→Parquet）耗时: 1.333s，吞吐 750235.79 rows/s
- D2 Parquet 大小: 26010015 bytes
- 两路径合计耗时: 2.732s
- 峰值 RSS: 882.38 MiB
- D1 行数校验: 1000000 rows, match=True
- D2 行数校验: 1000000 rows, match=True
- D2 schema: [{"name": "id", "type": "BIGINT"}, {"name": "customer_id", "type": "INTEGER"}, {"name": "amount", "type": "DECIMAL(12,2)"}, {"name": "created_at", "type": "TIMESTAMP"}, {"name": "status", "type": "VARCHAR"}, {"name": "payload", "type": "VARCHAR"}, {"name": "active", "type": "BOOLEAN"}]

## 结论与建议

- 对照结果见总报告 research-report.md 第 6 节（四路径对照表）。

## 参考资料

- 本任务 PRD: `prd.md`
- 原始指标: `pg_duckdb_metrics.json`
- 总报告: `../../research-report.md`
