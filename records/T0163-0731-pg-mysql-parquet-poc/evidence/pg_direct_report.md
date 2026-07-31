# PostgreSQL 流式直转 Parquet POC 报告（无 CSV 中间态）

## 调研目标

验证 psycopg2 服务端游标流式读取 + pyarrow 分批直写 Parquet 的直转路径，检验：
1. 转换瓶颈是否被消除（对比 CSV 中间态路径）。
2. NUMERIC 是否可通过 Decimal128 无损保真。
3. 峰值内存是否进一步下降（无 CSV 文件与 DataFrame 物化）。

## 方法

- 复用既有 `poc_orders` 表（1000000 行，与 CSV 路径同源同构）。
- psycopg2 server-side cursor（itersize=100000）流式读取，无 CSV 落盘。
- 每批构造显式 Arrow schema（amount=Decimal128(12,2)，created_at=timestamp[us]），pyarrow ParquetWriter 追加写。
- 压缩 zstd，Parquet format version 2.6，batch=100000。

## 发现

- 查询流式读取耗时: 7.112s
- Arrow 构造+Parquet 写入耗时: 7.096s
- 端到端耗时: 7.265s
- 端到端吞吐: 137653.13 rows/s
- 导出吞吐: 140610.14 rows/s
- 转换吞吐: 140918.57 rows/s
- Parquet 大小: 35971593 bytes
- 峰值 RSS: 876.68 MiB
- 行数校验: source=1000000, written=1000000, match=True
- Decimal128 保真: True

## 结论与建议

- 直转路径端到端显著快于 CSV 中间态路径，转换阶段瓶颈被消除（对照见总报告）。
- NUMERIC 通过 Decimal128(12,2) 无损落盘，类型保真风险消除。
- 无 CSV 文件、无 pandas DataFrame 物化，峰值内存下降。

## 参考资料

- 本任务 PRD: `prd.md`
- 原始指标: `pg_direct_metrics.json`
- 总报告: `../../research-report.md`
