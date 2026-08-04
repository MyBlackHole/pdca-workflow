# Parquet 文件格式深度技术调研 — 规格文档 (v2)

## 问题陈述

上一阶段完成了《Oracle 数据文件→Parquet 方案调研报告》，覆盖了从 Oracle 转换到 Parquet 的多种方案对比，并推荐了 Spark JDBC 路线。但报告中未深入覆盖 **Parquet 文件格式本身**的技术细节。

本阶段目标：对 Apache Parquet 列存格式进行系统性技术调研，产出多份独立专题文档，为后续迁移实施提供技术基础。

## 调研范围

覆盖以下 7 个子方向（全部覆盖，每方向产出独立专题文档）：

### 1. 文件物理结构 & 读写流程
- Parquet 文件的二进制布局：Magic bytes (PAR1)、Footer 元数据、Row Group / Column Chunk / Page 三层结构
- Dremel 编码原理：Repetition Level（重复级别）和 Definition Level（定义级别）如何编码嵌套数据
- 完整读写生命周期：从写入编码到读取解码的全链路

### 2. 编码 & 压缩深入
- 编码方式原理对比：PLAIN、RLE（Run-Length Encoding）、DELTA_BINARY_PACKED、DELTA_BYTE_ARRAY、DELTA_LENGTH_BYTE_ARRAY、BYTE_STREAM_SPLIT
- 各编码的适用场景和数据特征
- 压缩算法基准对比：Snappy / ZSTD / Gzip / LZ4 / Brotli
  - 压缩比 vs 压缩速度 vs 解压速度 的 trade-off
  - 各算法的推荐场景
- 编码 + 压缩的组合使用策略

### 3. 调优参数 & 性能优化
- 核心参数详解：Row Group Size、Page Size、Dictionary Page Size、Data Page Version
- Dictionary Encoding 的开启/关闭策略与阈值控制
- 各参数对文件大小、写入性能、读取性能、内存占用的影响
- Spark / PyArrow 写 Parquet 的最佳实践参数配置

### 4. Schema & 类型系统
- Parquet 物理类型（INT32/INT64/FLOAT/DOUBLE/BYTE_ARRAY/FIXED_LEN_BYTE_ARRAY）
- 逻辑类型（LogicalType / ConvertedType）映射体系：Decimal、Date/Time、Timestamp、String、UUID、JSON、BSON 等
- 嵌套结构的 Repetition 模型：REQUIRED / OPTIONAL / REPEATED
- Schema Evolution 兼容性：新增列、类型变更、列重命名、列删除
- Oracle 数据类型 → Parquet 逻辑类型的映射建议

### 5. SDK 生态对比
- **PyArrow / Arrow C++ (libparquet)**：功能特性、性能、Python 生态集成
- **parquet-mr (Java)**：Hadoop/Spark 生态中的定位
- **rust-parquet (Apache Arrow Rust)**：新兴高性能实现
- **其他语言绑定**：Node.js (parquetjs/parquets)、Go (parquet-go)、C# (Parquet.Net)
- 各 SDK 的功能完备度、性能对比、社区活跃度、维护状态
- 推荐 SDK 选型建议

### 6. Predicate Pushdown 原理
- 统计信息（ColumnIndex / OffsetIndex）的组织方式：min/max/null count 在 Page 级别和 Column Chunk 级别的存储
- Row Group 裁剪（Row Group Pruning）：通过 Footer 统计信息跳过不相关 Row Group
- Page Index 机制：1.0 新增的 Page 级别索引实现精细跳过
- 与查询引擎的集成：Spark / DuckDB / Arrow Dataset / parquet-cli 的谓词下推支持程度
- Bloom Filter 在 Parquet 中的应用

## 产出要求

- 格式：markdown 文档，每子方向一篇独立文档
- 存放位置：当前仓库 `/home/black/Public/aio/Idea/Parquet/` 下
- 命名风格：`parquet-<topic>.md`
- 内容要求：引用官方规范和数据支撑，避免无来源的主观判断

### 7. 生产案例 & 数据库转换实践
- **大规模生产案例调研**：
  - 各家公司（Uber/Netflix/Twitter/Apple 等）在生产中使用 Parquet 的实际规模和场景
  - Parquet 在数据湖（Delta Lake / Iceberg / Hudi）中的角色和案例
  - Parquet 在云数据仓库（Snowflake / Redshift Spectrum / BigQuery / Databricks）中的使用情况
- **踩坑与经验教训**：
  - 小文件问题（too many small files）及其治理方案
  - Schema Evolution 在生产中的兼容性踩坑
  - 编码/压缩选择不当导致的性能问题
  - Row Group 大小不合理引发的 OOM 或扫描性能下降
- **PostgreSQL → Parquet 转换实现说明**：
  - 方案选型对比：COPY 导出 + 转换 vs pg_dump + 解析 vs JDBC 直连导出 vs FDW 外部表
  - 每种方案的决策原因（适用场景、性能、类型保真度、运维成本）
  - 推荐方案实现细节：工具链、参数配置、并行策略
  - 数据类型映射：PostgreSQL 类型 → Parquet 逻辑类型
  - 大表分片策略（主键分片 vs 时间分片 vs 并行 pg_dump 作业）
  - 增量导出方案的可行性分析
- **MySQL → Parquet 转换实现说明**：
  - 方案选型对比：SELECT INTO OUTFILE + 转换 vs mysqldump + 解析 vs JDBC 直连导出 vs MySQL Shell 并行导出
  - 每种方案的决策原因（适用场景、性能、类型保真度、运维成本）
  - 推荐方案实现细节：工具链、参数配置、并行策略
  - 数据类型映射：MySQL 类型 → Parquet 逻辑类型
  - 大表分片策略（主键分片 vs 时间分区）
  - 增量导出方案的可行性分析
- **与 Oracle 方案对比总结**：
  - Oracle vs PostgreSQL vs MySQL → Parquet 的方案对比总表
  - 共通的最佳实践和差异化的处理方案

## 范围外

- 不涉及 Oracle .dbf 的再次分析（已在上一份报告中完成）
- 不涉及 Spark JDBC 导出代码实现（后续阶段处理）
- 不涉及 Parquet vs ORC vs Avro 的格式对比

## 验收标准

- [ ] 6 篇专题文档均完成且可独立阅读
- [ ] 每篇文档包含至少一个 ASCII/图表格式的结构示意
- [ ] 编码/压缩篇包含各算法的基准性能数据（引用权威来源）
- [ ] 调优篇包含具体可操作的参数推荐值
- [ ] SDK 篇包含功能矩阵对比表
- [ ] Schema 篇包含 Oracle 类型 → Parquet 类型的映射表
- [ ] 生产案例篇包含至少 3 家有据可查的规模案例和具体踩坑教训
- [ ] PostgreSQL 转换方案包含方案对比矩阵及推荐方案的详细实现说明
- [ ] MySQL 转换方案包含方案对比矩阵及推荐方案的详细实现说明
- [ ] 包含 Oracle / PostgreSQL / MySQL 三种数据库→Parquet 的方案对比总表
