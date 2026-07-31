# Parquet SDK 生态对比调研

> T0155 (子任务) — 父任务: T0150 (Parquet 格式深度技术调研)
> 更新日期: 2026-07-30

---

## 1. 概述

Apache Parquet 是一种列式存储格式，广泛应用于大数据和数据分析领域。本文从功能完备度、性能、生态集成、社区活跃度等维度对各语言 SDK 进行全面对比。

官方格式规范库: [apache/parquet-format](https://github.com/apache/parquet-format)
官方实现状态页: <https://parquet.apache.org/docs/file-format/implementationstatus/>

---

## 2. 核心 SDK 详解

### 2.1 PyArrow / Arrow C++ (libparquet)

| 属性 | 说明 |
|------|------|
| **仓库** | [apache/arrow](https://github.com/apache/arrow) (C++ 实现并入 Arrow 主仓库) |
| **原仓库** | [apache/parquet-cpp](https://github.com/apache/parquet-cpp) (已于 2024-05 归档) |
| **语言** | C++ (核心), Python (PyArrow 绑定) |
| **Stars** | Arrow: ~45k, parquet-cpp(归档): 448 |
| **维护状态** | ✅ 活跃, Apache 官方项目 |
| **许可证** | Apache 2.0 |

#### 功能完备度

- **读写**: 完整读写支持, 含 DataPage V1/V2
- **编码**: PLAIN, PLAIN_DICTIONARY, RLE, RLE_DICTIONARY, BIT_PACKED, DELTA_BINARY_PACKED, DELTA_LENGTH_BYTE_ARRAY, DELTA_BYTE_ARRAY, BYTE_STREAM_SPLIT
- **压缩**: Snappy, GZIP, Brotli, LZ4_RAW, ZSTD, LZ4(已弃用)
- **谓词下推**: 支持 Column 统计跳过, Page index 分页跳过; 不支持 Bloom filter 跳过
- **Schema Evolution**: 支持 schema 合并与版本兼容性
- **Page Index**: ✅ 完整支持 (自 Arrow 20.0)
- **Bloom Filter**: ✅ 支持读写 (自 Arrow 15.0)
- **Modular Encryption**: ✅ 完整支持
- **嵌套类型**: LIST, MAP, STRUCT 完整支持
- **逻辑类型**: 除 ENUM, UUID, BSON 外全部支持; 最新支持 GEOMETRY/GEOGRAPHY (Arrow 21.0)

#### Python 生态集成

```python
import pyarrow.parquet as pq
import pandas as pd

# 读取
table = pq.read_table("data.parquet")
df = table.to_pandas()

# 写入
pq.write_table(table, "output.parquet", compression="zstd")

# 分区数据集
dataset = pq.ParquetDataset("dataset_path/")
table = dataset.read(columns=["col1", "col2"], filters=[("col1", ">", 100)])

# DuckDB 集成
import duckdb
duckdb.sql("SELECT * FROM 'data.parquet'")
```

- pandas: 原生零拷贝转换
- numpy: Arrow 数组可直接转为 numpy 数组
- DuckDB: 原生支持直接查询 parquet 文件
- Dask: 通过 `dask.dataframe.read_parquet` 使用 PyArrow 引擎

#### 适用场景

最高推荐。Python 数据科学生态的标准方案; C++ 集成引擎的最佳选择。

---

### 2.2 parquet-mr (Java)

| 属性 | 说明 |
|------|------|
| **仓库** | [apache/parquet-java](https://github.com/apache/parquet-java) |
| **原名称** | parquet-mr |
| **语言** | Java |
| **Stars** | 3.1k |
| **维护状态** | ✅ 活跃, Apache 官方项目 |
| **最新版本** | 1.17.0 |
| **许可证** | Apache 2.0 |

#### 功能完备度

- 功能特性与 C++ 实现基本一致
- **独特优势**: 支持 JAVA Vector API (实验性, 需要 AVX-512)
- **Java 生态集成**: Hadoop Input/Output Format, Hive, Pig, Cascading, Crunch, Avro, Thrift, Protocol Buffers
- **谓词下推**: 支持 Row group 统计跳过、Bloom filter 跳过、Page 统计跳过
- **支持 Column index**: ✅
- **Page index**: ✅

#### 与 C++ 实现的差异

| 维度 | parquet-mr (Java) | Arrow C++ |
|------|-------------------|-----------|
| 性能 | JVM GC 开销; 向量化实验性 | 原生 SIMD, 零拷贝 |
| 生态 | Hadoop/Spark 供应链标准 | Python 数据科学、Arrow 生态 |
| 部署 | 依赖 JVM | 轻量级无运行时依赖 |
| Bloom filter 跳过 | ⚠️ 仅写, 无读 | ✅ 完整支持 |

#### 在查询引擎中的角色

- **Apache Spark SQL**: 默认的 Parquet 实现, 通过 `spark.sql.parquet` 配置
- **Apache Hive**: 默认的列式存储格式
- **Presto / Trino**: 原生支持读取
- **Apache Flink**: 通过 parquet-java 读写
- **Apache Cassandra**: 支持导出为 Parquet

#### 适用场景

Hadoop/Spark 生态系统的必备组件。如果 JVM 栈是技术基础, 这是默认选择。

---

### 2.3 rust-parquet (Apache Arrow Rust)

| 属性 | 说明 |
|------|------|
| **仓库** | [apache/arrow-rs](https://github.com/apache/arrow-rs) |
| **Crate** | `parquet` (crates.io) |
| **语言** | Rust |
| **Stars** | 3.6k |
| **维护状态** | ✅ 活跃, Apache 官方, 约月度发布 |
| **最新版本** | 59.x 系列 (2026) |
| **许可证** | Apache 2.0 |

#### 功能完备度

- **读写**: 完整支持
- **编码**: 除 BIT_PACKED 外全部支持; 最新支持 BYTE_STREAM_SPLIT (v52.2+)
- **压缩**: Snappy, GZIP, Brotli, LZ4, LZ4_RAW, ZSTD
- **谓词下推**: Row group 统计跳过 ✅, Bloom filter 跳过 ✅, Page 统计跳过 ✅
- **Bloom filter**: ✅ 完整支持
- **Page index**: ✅
- **Modular Encryption**: ✅ 读支持 (v55.0), R 写支持 (v54.3)
- **Variant 类型**: ✅ (v56.0)
- **GEOMETRY/GEOGRAPHY**: ✅ (v57.0)
- **逻辑类型**: 基本完整, 部分类型(ENUM/UUID/JSON/BSON)仅按物理类型读取

#### 与 DataFusion / Ballista 的集成

- **Apache DataFusion**: Rust 原生查询引擎, 使用 arrow-rs 作为底层列式格式, 原生支持读写 Parquet
- **Apache Ballista**: 分布式计算引擎, 基于 DataFusion 和 arrow-rs
- 三者形成完整的 Rust 大数据栈: 存储(Parquet) → 内存(Arrow) → 计算(DataFusion) → 分布式(Ballista)

```rust
use parquet::file::reader::FileReader;
use parquet::file::reader::SerializedFileReader;
use std::fs::File;

let file = File::open("data.parquet").unwrap();
let reader = SerializedFileReader::new(file).unwrap();
let metadata = reader.metadata();
```

#### 适用场景

Rust 原生高性能场景, 需要内存安全和并发优势的管线, DataFusion/Ballista 用户。

---

### 2.4 Apache Arrow Go (arrow-go)

| 属性 | 说明 |
|------|------|
| **仓库** | [apache/arrow-go](https://github.com/apache/arrow-go) |
| **语言** | Go |
| **Stars** | 390 |
| **维护状态** | ✅ 活跃, Apache 官方 |
| **最新版本** | v18.x 系列 |
| **许可证** | Apache 2.0 |

#### 功能完备度

- **编码**: 全面支持, 含 BYTE_STREAM_SPLIT (v18.0+)
- **压缩**: Snappy, GZIP, Brotli, LZ4_RAW, ZSTD
- **Bloom filter**: ✅ (v18.3+)
- **Modular Encryption**: ✅
- **Variant**: ✅ (v18.4)
- **Page index**: ✅
- **逻辑类型**: 全面支持; 部分缺失: BSON, GEOMETRY, GEOGRAPHY

#### 适用场景

Go 微服务中的轻量级列式存储; 需要在 Go 生态中使用 Parquet 的最佳官方选择。

---

### 2.5 Go: fraugster/parquet-go

| 属性 | 说明 |
|------|------|
| **仓库** | [fraugster/parquet-go](https://github.com/fraugster/parquet-go) |
| **语言** | Go |
| **Stars** | 289 |
| **维护状态** | ⚠️ 低活跃 |
| **许可证** | Apache 2.0 |

功能较 arrow-go 有限:
- 不支持 Byte Stream Split 编码
- 不支持 Index Pages
- 不支持 Encryption
- 不支持 Bloom Filter
- 压缩: 仅 GZIP 和 Snappy 内置, Brotli/LZ4_RAW/ZSTD/LZO 需额外导入
- 逻辑类型支持基本完整

**不推荐新项目使用**, 建议迁移到 arrow-go。

---

### 2.6 Node.js: parquetjs / parquets

| 库 | 仓库 | Stars | 状态 | 功能 |
|----|------|-------|------|------|
| **parquetjs** | npm `parquetjs` | ~200 | ⚠️ 低维护 | 基本读写, PLAIN/RLE, Snappy/GZIP |
| **parquets** | npm `parquets` | ~100 | ⚠️ 低维护 | 基本读写, 功能受限 |
| **hyparquet** | [hyparam/hyparquet](https://github.com/hyparam/hyparquet) | 较新 | ✅ 活跃 | JS 实现, 支持全类型压缩编码 |

Node.js 生态缺乏官方的成熟 Parquet 实现。`hyparquet` 是较新且活跃的 JS 实现。

#### 适用场景

仅当 Node.js 必须直接读写 Parquet 时的备选方案; 优先通过 DuckDB WASM 或 PyArrow 微服务桥接。

---

### 2.7 C#: Parquet.Net

| 属性 | 说明 |
|------|------|
| **仓库** | [aloneguid/parquet-dotnet](https://github.com/aloneguid/parquet-dotnet) |
| **语言** | C# |
| **Stars** | 859 |
| **维护状态** | ✅ 活跃, 非官方但广泛使用 |
| **最新版本** | 5.6.x / 6.0.0-pre |
| **许可证** | MIT |
| **NuGet 下载** | 数千万次 |

#### 功能特性

- 纯托管 .NET 实现 (非 C++ 封装)
- 支持动态 schema
- 所有 Parquet 类型、编码和压缩
- C# 类序列化 (含复杂嵌套类型)
- 低层级/高层级/无类型 API
- `Microsoft.Data.Analysis` DataFrame 集成
- 多平台: Linux, macOS, Windows, iOS, Android

#### 适用场景

.NET 生态的首选方案。在 .NET 大数据场景中值得推荐。

> 另有 **ParquetSharp**: P/Invoke 封装 parquet-cpp, 性能接近原生 C++, 但部署依赖原生库。

---

### 2.8 C: libparquet C 接口

| 属性 | 说明 |
|------|------|
| **位置** | Arrow C++ 的一部分 |
| **接口** | parquet-glib (C GLib), parquet C ABI |
| **状态** | ✅ 通过 Arrow C++ 提供 |

C 接口作为其他语言绑定的基础层:
- **ParquetSharp (.NET)**: 通过 P/Invoke 调用 C 接口
- **C GLib**: 通过 GObject 类型系统暴露
- 性能接近 C++, 但 API 较为底层

---

## 3. 功能矩阵对比表

### 3.1 基础功能对比

| 功能 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net | fraugster-go | parquetjs | hyparquet |
|------|:-----------:|:------------:|:--------:|:--------:|:-----------:|:------------:|:---------:|:---------:|
| **语言** | C++/Python | Java | Rust | Go | C# | Go | JS | JS |
| **维护状态** | ✅ 活跃 | ✅ 活跃 | ✅ 活跃 | ✅ 活跃 | ✅ 活跃 | ⚠️ 低 | ⚠️ 低 | ✅ 活跃 |
| **Apache 官方** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **读支持** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **写支持** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **DataPage V1** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **DataPage V2** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **嵌套类型** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 部分 | ✅ |
| **Schema Evolution** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

### 3.2 编码支持

| 编码 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net | fraugster-go | hyparquet |
|------|:-----------:|:------------:|:--------:|:--------:|:-----------:|:------------:|:---------:|
| PLAIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PLAIN_DICTIONARY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RLE_DICTIONARY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RLE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| BIT_PACKED | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| DELTA_BINARY_PACKED | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DELTA_LENGTH_BYTE_ARRAY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DELTA_BYTE_ARRAY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| BYTE_STREAM_SPLIT | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |

### 3.3 压缩支持

| 压缩 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net | fraugster-go | hyparquet |
|------|:-----------:|:------------:|:--------:|:--------:|:-----------:|:------------:|:---------:|
| Snappy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GZIP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Brotli | ✅ | ✅ | ✅ | ✅ | ✅ | 需要额外包 | ❌ |
| LZ4_RAW | ✅ | ✅ | ✅ | ✅ | ✅ | 需要额外包 | ❌ |
| ZSTD | ✅ | ✅ | ✅ | ✅ | ✅ | 需要额外包 | ❌ |
| LZO | ❌ | ❌ | ❌ | ❌ | ❌ | 需要额外包 | ❌ |

### 3.4 高级功能

| 功能 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net | hyparquet |
|------|:-----------:|:------------:|:--------:|:--------:|:-----------:|:---------:|
| Page Index | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Bloom Filter (读) | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Bloom Filter (写) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modular Encryption | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Page CRC32 | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Row group 统计跳过 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Page 统计跳过 | ❌ | ✅ | ✅ | 部分 | ❌ | ✅ |
| Bloom filter 跳过 | ❌ | ✅ | ✅ | 部分 | ❌ | ✅ |
| Column index | ✅ | ✅ | ✅ | ✅ | 部分 | ✅ |
| Size statistics | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Variant 类型 ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| GEOMETRY/GEOGRAPHY | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |

### 3.5 逻辑类型支持

| 逻辑类型 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net | hyparquet |
|----------|:-----------:|:------------:|:--------:|:--------:|:-----------:|:---------:|
| STRING | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ENUM | ❌ | ✅ | 仅物理 | ✅ | ✅ | ✅ |
| UUID | ❌ | ✅ | 仅物理 | ✅ | ✅ | ✅ |
| INT (signed/unsigned) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DECIMAL (INT32/64) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DECIMAL (FLBA) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DECIMAL (BYTE_ARRAY) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FLOAT16 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| DATE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TIME (INT32/64) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TIMESTAMP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| INTERVAL | ✅ | 仅物理 | ✅ | ✅ | ❌ | ✅ |
| JSON | ✅ | 仅物理 | 仅物理 | ✅ | ✅ | ✅ |
| BSON | ❌ | 仅物理 | 仅物理 | ❌ | ❌ | ❌ |
| VARIANT | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| GEOMETRY/GEOGRAPHY | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| LIST | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MAP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 3.6 社区与性能指标

| 指标 | PyArrow/C++ | parquet-java | arrow-rs | arrow-go | Parquet.Net |
|------|:-----------:|:------------:|:--------:|:--------:|:-----------:|
| **GitHub Stars** | 45k (Arrow) | 3.1k | 3.6k | 390 | 859 |
| **贡献者** | 1000+ | 200+ | 500+ | 80+ | 100+ |
| **Commits** | 50k+ (Arrow) | 2,994 | 7,894 | 1,323 | 3,500+ |
| **最新版本** | Arrow 25.0 | 1.17.0 | 59.x | v18.x | 5.6.x |
| **发布频率** | 月 | 季度 | 月 | 月 | 季度 |
| **读性能** | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **写性能** | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| **内存效率** | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |

---

## 4. 推荐选型建议

### 场景一: Python 数据科学 / ML 管线

**首选: PyArrow**

理由: Python 生态的标准选择, pandas/numpy/DuckDB 深度集成, 功能最完整。

### 场景二: Java / JVM 大数据平台

**首选: parquet-java**

理由: Spark/Hive/Flink/Presto 的标准组件, JVM 生态不可替代。

### 场景三: Rust 高性能计算 / 新系统构建

**首选: arrow-rs (parquet crate)**

理由: 内存安全、性能卓越、与 DataFusion/Ballista 构成完整大数据栈。

### 场景四: Go 微服务 / 工具开发

**首选: arrow-go**

理由: Apache 官方 Go 实现, 功能较完整, 性能良好。

### 场景五: .NET / C# 应用

**首选: Parquet.Net**

理由: 纯托管实现, 功能完整, 活跃维护, 千万级 NuGet 下载量。

### 场景六: Node.js / TypeScript 应用

**首选: hyparquet** (或通过 DuckDB WASM 桥接)

理由: Node.js 生态缺乏官方 SDK; hyparquet 是最活跃的 JS 实现。

### 场景七: 嵌入式 / IoT / 底层系统

**首选: Arrow C++ 或 arrow-rs**

理由: 无运行时依赖, 最小化资源占用, 极致性能。

---

## 5. 总结

| 维度 | 冠军 | 理由 |
|------|------|------|
| **功能最完整** | PyArrow / Arrow C++ | 格式标准的最完整实现 |
| **生态最广泛** | parquet-java | Hadoop/Spark 供应链基石 |
| **性能最佳** | Arrow C++ / arrow-rs | SIMD 优化, 零拷贝设计 |
| **最快演进** | arrow-rs | 月发布周期, 新格式特性优先落地 |
| **最佳跨语言** | PyArrow | Python 数据科学生态枢纽 |
| **最佳 .NET 方案** | Parquet.Net | 唯一成熟的纯 C# 实现 |

**总体建议**: 新项目优先选择 Apache Arrow 生态的 SDK (C++/Rust/Go), 它们对 Parquet 格式新特性的支持最快且最一致。JVM 项目则无悬念选择 parquet-java。
