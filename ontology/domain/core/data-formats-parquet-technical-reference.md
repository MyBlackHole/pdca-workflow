---
schema: pdca.asset/v1
id: ontology:domain/data-formats-parquet-technical-reference
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats-parquet-technical-reference/1.0.0
summary: Parquet 技术参考索引
domain:
- ontology:domain/data-formats
relations:
  specializes:
  - ontology:domain/data-formats
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'Parquet 技术参考索引' ontology/domain/core/data-formats-parquet-technical-reference.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# Parquet 技术参考索引

## 来源
- 记录: `records/T0150/conclusion.md`
- 任务: T0150 Parquet 文件格式深度技术调研

## 专题文档

| # | 主题 | 文件 | 内容要点 |
|---|------|------|---------|
| 1 | 文件物理结构 & 读写流程 | `parquet-physical-structure.md` | 二进制布局、Dremel 编码、读写全生命周期 |
| 2 | 编码 & 压缩深入 | `parquet-encoding-compression.md` | 7 种编码原理、5 种压缩算法基准对比、组合策略 |
| 3 | 调优参数 & 性能优化 | `parquet-tuning.md` | Row Group/Page/Dictionary 参数推荐值 |
| 4 | Schema & 类型系统 | `parquet-schema-types.md` | 物理/逻辑类型、嵌套模型、Oracle 映射 |
| 5 | SDK 生态对比 | `parquet-sdk-ecosystem.md` | PyArrow/parquet-mr/rust-parquet 等功能矩阵 |
| 6 | Predicate Pushdown 原理 | `parquet-predicate-pushdown.md` | 统计信息、Row Group 裁剪、Page Index、Bloom Filter |
| 7 | 生产案例 & 数据库转换 | `parquet-production-cases.md` | 规模案例、踩坑教训、PG/MySQL 转换方案 |

## 关键结论
- **推荐 SDK**: PyArrow（Python 生态首选）、parquet-mr（Spark/Hadoop 生态）
- **推荐编码**: DELTA_BINARY_PACKED（数值列）、RLE（低基数列）、PLAIN（兜底）
- **推荐压缩**: ZSTD（平衡型）、Snappy（速度优先）
- **推荐 Row Group Size**: 128MB~512MB（平衡读写性能）
- **类型映射**: Oracle/PostgreSQL/MySQL → Parquet 均有完整映射表

## 适用场景
数据库数据迁移到 Parquet 列存格式的技术参考。文档存放于项目仓库。

## 后续方向
- Spark JDBC Oracle→Parquet 原型实现
- PG/MySQL 转换 PoC 验证
