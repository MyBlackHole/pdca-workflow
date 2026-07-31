# Parquet 生产案例 & 数据库转换实践

## 范围
- 大规模生产案例：Uber/Netflix/Twitter/Apple 等公司的 Parquet 使用规模和场景
- Parquet 在数据湖（Delta Lake / Iceberg / Hudi）中的角色
- Parquet 在云数仓（Snowflake / Redshift Spectrum / BigQuery / Databricks）中的使用
- 踩坑经验：小文件问题、Schema Evolution 兼容性、编码压缩选择、OOM 问题
- PostgreSQL → Parquet 方案对比矩阵及推荐实现（含决策原因、类型映射、分片策略）
- MySQL → Parquet 方案对比矩阵及推荐实现（含决策原因、类型映射、分片策略）
- Oracle / PostgreSQL / MySQL → Parquet 方案对比总表
