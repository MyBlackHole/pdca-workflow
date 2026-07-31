# Parquet Schema & 类型系统

## 范围
- 物理类型：INT32/INT64/FLOAT/DOUBLE/BYTE_ARRAY/FIXED_LEN_BYTE_ARRAY
- 逻辑类型：LogicalType / ConvertedType 映射体系（Decimal、Date/Time、Timestamp、String、UUID、JSON、BSON 等）
- 嵌套结构 Repetition 模型：REQUIRED / OPTIONAL / REPEATED
- Schema Evolution 兼容性：新增列、类型变更、列重命名、列删除
- Oracle 类型 → Parquet 逻辑类型的映射建议表
