---
schema: pdca.asset/v1
id: T0150
phase: check
source_ids:
  - phy-struct
  - enc-comp
  - tuning
  - schema
  - sdk
  - pred-pd
  - prod-cases
---

## 上下文

本任务为 Oracle 数据文件→Parquet 方案调研的延续阶段。上一阶段产出了《Oracle 数据文件→Parquet 方案调研报告》并推荐了 Spark JDBC 路线。本阶段对 Apache Parquet 列存格式本身进行系统性技术调研。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| Parquet 文件结构可通过官方规范系统性理解 | 已验证 | phy-struct |
| 编码和压缩算法有明确的权衡和选型依据 | 已验证 | enc-comp |
| 调优参数有可操作的推荐值 | 已验证 | tuning |
| Schema 类型系统及 Oracle 映射可完整梳理 | 已验证 | schema |
| SDK 生态可通过功能矩阵对比指导选型 | 已验证 | sdk |
| Predicate Pushdown 原理可清晰解释性能优势 | 已验证 | pred-pd |
| PostgreSQL/MySQL 转换方案可参照 Oracle 方案推导实践 | 已验证 | prod-cases |

## 分析

7 篇专题文档全面覆盖了 Parquet 格式的核心技术维度。调研方法包括：
- 查阅 Apache Parquet 官方格式规范（Thrift 定义）
- 引用 Google Dremel 论文（原始列存编码理论）
- 参考各压缩算法官方 benchmark 数据
- 收集公开生产案例（Uber/Netflix/Twitter/LinkedIn/Apple/Spotify）
- 对比 PostgreSQL/MySQL 转换方案并形成三库方案总结

所有验收标准已通过 convergence map 验证。

## 适用边界

- 本调研聚焦 Parquet 格式本身，不涉及具体编码实现（代码示例仅用于说明）
- PostgreSQL/MySQL 转换方案为调研分析，未经过实际生产验证
- 压缩算法数据引用公开 benchmark，实际性能因环境而异

## 下一轮建议

后续可考虑：
1. 基于 Spark JDBC 推荐方案实现 Oracle→Parquet 原型工具
2. PostgreSQL/MySQL 转换方案的 PoC 验证
3. Parquet 与 ORC、Avro 等格式的横向对比调研
