# AC-5 四路径 1M 性能对照（≥3 轮流中位数，ZSTD 写出）

## 环境
- MySQL 8.0（t0250-mysql8:3307）poc_orders 1M 行 / PG 18（t0216-pg:5433）poc_orders 1M 行
- 物理直读：build/mysqlbin（.ibd→parquet）、build/pgbin（heap+pg_xact→parquet）
- DuckDB scanner：duckdb 1.5.5 py（mysql_scanner / postgres_scanner 插件）
- 数据源：mysqlbin 读 `evidence/mysql/poc_orders.ibd`（138MB, 8448 页）；
  pgbin 读 PG heap 快照 poc_heap(136MB)+CLOG
- 行数校验：四路径输出 parquet rows=1,000,000 全部一致

## 中位数结果（3 轮）

| 路径 | 中位耗时 s | 吞吐 rows/s | 峰值 RSS | Parquet 大小 |
|---|---|---|---|---|
| MySQL 物理直读 (M-phys) | 1.789 | 558,985 | 1138 MB | 22.7 MB |
| PG 物理直读 (P-phys) | 1.061 | 942,288 | 307 MB | 24.8 MB |
| DuckDB mysql_scanner (M-duck) | 4.640 | 215,528 | 54 MB | 45.7 MB |
| DuckDB postgres_scanner (P-duck) | 1.301 | 768,405 | 54 MB | 49.4 MB |

注：M-phys RSS 高因 mmap 整 138MB ibd + Arrow 写出缓冲；吞吐含进程启动开销。
三种实现产出 Parquet 大小差异：物理直读利用列类型映射（decimal128/ timestamp us/boolean）压缩更小，
DuckDB scanner 为通用 VARCHAR 物化（约 2 倍空间）。

## 单轮明细
- M-phys s: 1.711 / 1.789 / 1.867
- P-phys s: 1.061 / 0.990 / 1.073
- M-duck s: 4.584 / 4.640 / 4.657
- P-duck s: 1.301 / 1.347 / 1.256
