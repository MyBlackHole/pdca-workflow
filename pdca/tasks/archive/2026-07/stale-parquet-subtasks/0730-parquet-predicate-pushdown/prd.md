# Parquet Predicate Pushdown 原理

## 范围
- 统计信息组织：ColumnIndex / OffsetIndex 的存储结构
- min/max/null count 在 Page 级别和 Column Chunk 级别的存储
- Row Group 裁剪（Row Group Pruning）原理
- Page Index 机制（Parquet 1.0+）
- 与查询引擎集成：Spark / DuckDB / Arrow Dataset / parquet-cli 的谓词下推支持
- Bloom Filter 在 Parquet 中的应用
