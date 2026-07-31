# PostgreSQL 数据文件直接转 Parquet POC 报告（物理路径）

## 调研目标

验证绕开 SQL 服务层的物理路径：用 pg_filedump 直接解析 PG heap 数据文件并转 Parquet，
对照逻辑路径（COPY/查询流式）评估吞吐、可行性和限制。

## 方法

- 源数据: `/tmp/opencode/pgfiledump-test/poc_orders_heap`（poc_orders 的 main fork，136536064 bytes，CHECKPOINT 后从容器拷出）。
- 解码: `pg_filedump -D bigint,int,numeric,timestamp,text,text,bool <heap>` → COPY 风格 TSV。
- 预处理: 剥离每行 `COPY: ` 前缀。
- 转换: DuckDB read_csv(TSV) → PARQUET ZSTD（显式 Decimal128(12,2)）。

## 发现

- pg_filedump 解码耗时: 1.465s，吞吐 682808.81 rows/s
- 解码 TSV 大小: 197241611 bytes
- 前缀清理耗时: 0.631s
- DuckDB 转换耗时: 1.166s
- 端到端耗时: 3.323s，吞吐 300927.30 rows/s
- Parquet 大小: 26020890 bytes
- 峰值 RSS: 911.25 MiB
- 行数校验: source=1000000, parquet=1000000, match=True
- schema: [{"name": "id", "type": "BIGINT"}, {"name": "customer_id", "type": "INTEGER"}, {"name": "amount", "type": "DECIMAL(12,2)"}, {"name": "created_at", "type": "TIMESTAMP"}, {"name": "status", "type": "VARCHAR"}, {"name": "payload", "type": "VARCHAR"}, {"name": "active", "type": "BOOLEAN"}]

## 结论与建议

- 物理路径可行且不依赖运行中的 PG 服务（可用于冷备份/离线迁移场景）。
- 吞吐与限制对照见总报告 research-report.md 第 6 节。

## 参考资料

- 本任务 PRD: `prd.md`
- 原始指标: `pg_filedump_metrics.json`
- 总报告: `../../research-report.md`
