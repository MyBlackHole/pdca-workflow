# Parquet 文件物理结构与读写流程深度解析

> **调研说明**：本文档基于 Apache Parquet 官方格式规范 v2.x，聚焦物理存储布局与数据读写全生命周期，包含二进制布局、三层结构、Dremel 编码原理及完整的读写流程。

---

## 目录

1. [文件整体二进制布局](#1-文件整体二进制布局)
2. [Footer 元数据结构详解](#2-footer-元数据结构详解)
3. [Row Group / Column Chunk / Page 三层结构](#3-row-group--column-chunk--page-三层结构)
4. [Dremel 编码原理](#4-dremel-编码原理)
5. [完整读写生命周期](#5-完整读写生命周期)
6. [参考资料](#6-参考资料)

---

## 1. 文件整体二进制布局

### 1.1 文件构成总览

一个 Parquet 文件的二进制布局分为三个主要区域：

```
┌─────────────────────────────────────────────────────────────┐
│                       Parquet 文件                           │
├─────────────────────────────────────────────────────────────┤
│  Magic Bytes (4B)           "PAR1"                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     Row Group 数据区域                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Row Group 1                                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐              │   │
│  │  │ Col 1    │ │ Col 2    │ │ Col 3    │  ...         │   │
│  │  │ Chunk A  │ │ Chunk B  │ │ Chunk C  │              │   │
│  │  │ ┌──┬──┬──┐│ ┌──┬──┬──┐│ ┌──┬──┬──┐               │   │
│  │  │ │D │P1│P2││ │D │P1│P2││ │D │P1│P2│               │   │
│  │  │ │Pg│g │g ││ │Pg│g │g ││ │Pg│g │g │               │   │
│  │  │ └──┴──┴──┘│ └──┴──┴──┘│ └──┴──┴──┘               │   │
│  │  └──────────┘ └──────────┘ └──────────┘              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Row Group 2                  ...                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                             ...                              │
├─────────────────────────────────────────────────────────────┤
│  Footer Section                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FileMetaData (Thrift Compact Protocol)                │  │
│  │  ├── schema: list<SchemaElement>                      │  │
│  │  ├── num_rows: int64                                  │  │
│  │  ├── row_groups: list<RowGroupMetaData>               │  │
│  │  │   ├── columns: list<ColumnChunkMetaData>           │  │
│  │  │   │   ├── type / encodings / path                  │  │
│  │  │   │   ├── page_offset / num_values                 │  │
│  │  │   │   ├── statistics (min/max/null_count)          │  │
│  │  │   │   └── total_compressed_size / total_uncompressed│  │
│  │  │   ├── num_rows: int64                              │  │
│  │  │   └── total_byte_size: int64                       │  │
│  │  ├── key_value_metadata: list<KeyValue>               │  │
│  │  ├── created_by: string                               │  │
│  │  └── column_orders: list<ColumnOrder>                 │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  Footer Metadata Length (4B)  little-endian int32     │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  Magic Bytes (4B)           "PAR1"                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Magic Bytes

```
偏移量 0x00:  50 41 52 31    ASCII "PAR1"
偏移量 end-4:  50 41 52 31    ASCII "PAR1"
```

- 文件开头 4 字节：`PAR1`（0x50 0x41 0x52 0x31）
- 文件末尾 4 字节：`PAR1`（同一签名）
- 这允许工具通过检查文件头部和尾部来快速识别 Parquet 文件

### 1.3 Footer 结构

Footer 紧接在最后一个 Row Group 之后，其结构为分层嵌套：

```
┌──────────────────────────────────────────┐
│  FileMetaData                            │
│  (Thrift Compact Protocol 序列化)        │
│                                           │
│  长度 = N bytes                           │
├──────────────────────────────────────────┤
│  Footer 长度 (4 bytes)                    │
│  little-endian int32 = N                 │
├──────────────────────────────────────────┤
│  Magic Bytes "PAR1" (4 bytes)            │
└──────────────────────────────────────────┘
```

**读取算法**：
1. 定位到文件末尾倒数 4 字节，验证 `PAR1` 签名
2. 向前读 4 字节，解析为 little-endian int32 → 得到 FileMetaData 长度 `N`
3. 定位到 `file_size - 8 - N`，读取 `N` 字节的 FileMetaData
4. 用 Thrift Compact Protocol 反序列化 FileMetaData

---

## 2. Footer 元数据结构详解

所有元数据使用 **Apache Thrift Compact Protocol** 序列化。Compact Protocol 是 Thrift 的一种变长编码协议，相比 Binary Protocol 可节省约 50% 的空间。

### 2.1 FileMetaData

```thrift
struct FileMetaData {
  1: required int32 version                  // 格式版本号（1 或 2）
  2: required list<SchemaElement> schema      // Schema 定义树
  3: required int64 num_rows                 // 文件总行数
  4: required list<RowGroup> row_groups      // 所有 Row Group 元数据
  5: optional list<KeyValue> key_value_metadata  // 自定义键值元数据
  6: optional string created_by              // 创建工具标识
  7: optional list<ColumnOrder> column_orders   // 列排序信息（v2+）
  8: optional list<PageHeader> page_headers     // 可选的所有 PageHeader 索引
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | int32 | 格式版本号。1 = 原始格式，2 = 支持 Page 级别校验和 |
| `schema` | list\<SchemaElement\> | Schema 树的先序遍历，每个元素描述一个字段 |
| `num_rows` | int64 | 文件中所有行的总数 |
| `row_groups` | list\<RowGroup\> | 所有 Row Group 的描述，实际数据不在此 |
| `key_value_metadata` | list\<KeyValue\> | 应用层自定义元数据（如 schema 版本、数据源标签） |
| `created_by` | string | 创建此文件的库/工具标识（如 `parquet-mr version 1.12.0`） |
| `column_orders` | list\<ColumnOrder\> | v2 引入，指明列的排序顺序（用于谓词下推优化） |

### 2.2 SchemaElement

```thrift
struct SchemaElement {
  1: optional Type type                      // 数据类型（BOOLEAN, INT32, INT64 等）
  2: required i32 type_length                // 固定长度类型的长度
  3: optional FieldRepetitionType repetition_type  // REQUIRED / OPTIONAL / REPEATED
  4: required string name                    // 字段名
  5: optional i32 num_children               // 子节点数（嵌套类型使用）
  6: optional list<ConvertedType> converted_type   // 逻辑类型（已弃用，v2 用 logicalType）
  7: optional i32 scale                      // DECIMAL 精度
  8: optional i32 precision                  // DECIMAL 标度
  9: optional i32 field_id                   // 字段 ID（Schema 演进用）
  10: optional LogicalType logicalType       // v2 逻辑类型（替代 converted_type）
}
```

Schema 以**先序遍历（pre-order traversal）**的扁平列表存储。对于嵌套字段，子字段紧随父字段之后。

**示例**：Schema `message Document { required int64 id; optional group Address { optional string city; optional string zip; } }`

序列化为：
```
Index 0: {name: "Document", num_children: 2, repetition_type: REQUIRED}  // Root message
Index 1: {name: "id", type: INT64, repetition_type: REQUIRED}
Index 2: {name: "Address", num_children: 2, repetition_type: OPTIONAL}   // Group node
Index 3: {name: "city", type: BYTE_ARRAY, repetition_type: OPTIONAL}
Index 4: {name: "zip", type: BYTE_ARRAY, repetition_type: OPTIONAL}
```

### 2.3 RowGroupMetaData (RowGroup)

```thrift
struct RowGroup {
  1: required list<ColumnChunk> columns        // 此 Row Group 包含的所有列块
  2: required int64 total_byte_size            // 所有列块的总字节数（压缩前）
  3: required int64 num_rows                   // 此 Row Group 中的行数
  4: optional int16 sorting_columns            // 排序列索引（v2，支持有序 Row Group）
  5: optional int64 file_offset                // v2 新增，文件内偏移（当前未使用）
  6: optional int64 total_compressed_size      // 所有列块的压缩后总字节数
  7: optional int16 ordinal                    // Row Group 序号
}
```

**Row Group 的关键设计点**：

| 属性 | 说明 |
|------|------|
| **num_rows** | 每个 Row Group 包含的行数。典型值：从数十万到数千万不等 |
| **total_byte_size** | 所有列未压缩的数据大小总和（累加每个 ColumnChunk 的未压缩大小） |
| **file_offset** | v2 预留字段，未来用于支持 Row Group 级别的文件偏移定位 |
| **columns** | 通常等于 Schema 中的叶子列数。如果启用了列裁剪，可能少于叶子列数 |

> **典型 Row Group 大小**：Apache 官方建议 512MB ～ 1GB（未压缩大小）。较小的 Row Group（< 128MB）会导致元数据膨胀和读取效率降低；过大的 Row Group（> 2GB）会增加内存压力和随机读取的粒度。

### 2.4 ColumnChunkMetaData (ColumnChunk)

```thrift
struct ColumnChunk {
  1: required string file_path                 // 文件路径（行组拆分到多个文件时使用）
  2: required ColumnMetaData meta_data         // 列块元数据
  3: optional int64 file_offset                // 列块数据的起始文件偏移
  4: optional int64 offset_index_offset        // v2，OffsetIndex 在文件中的偏移
  5: optional int64 offset_index_length        // v2，OffsetIndex 的长度
  6: optional int64 column_index_offset        // v2，ColumnIndex 在文件中的偏移
  7: optional int64 column_index_length        // v2，ColumnIndex 的长度
  8: optional list<Chunk> encrypted_metadata   // v2，加密元数据
}
```

```thrift
struct ColumnMetaData {
  1: required Type type                        // 物理类型（BOOLEAN, INT32, INT64, INT96, FLOAT, DOUBLE, BYTE_ARRAY, FIXED_LEN_BYTE_ARRAY）
  2: required list<Encoding> encodings         // 此列块使用的所有编码类型
  3: required list<string> path_in_schema      // Schema 路径（如 ["Address", "city"]）
  4: required list<PageType> codec             // 压缩编解码器（UNCOMPRESSED, SNAPPY, GZIP, LZO, BROTLI, LZ4, ZSTD, LZ4_RAW）
  5: required int64 num_values                 // 此列块中的总 value 数（编码后不会变）
  6: required int64 total_uncompressed_size    // 此列块未压缩的总字节数
  7: required int64 total_compressed_size      // 此列块压缩后的总字节数
  8: required int64 data_page_offset           // 第一页数据在文件中的偏移
  9: optional int64 index_page_offset          // Index Page 的偏移（如果有）
  10: optional int64 dictionary_page_offset    // Dictionary Page 的偏移（如果有）
  11: optional Statistics statistics           // 列统计信息（min, max, null_count, distinct_count）
  12: optional list<Encoding> bloom_filter     // Bloom Filter（v2 可选）
}
```

**Statistics 结构**（用于谓词下推）：

```thrift
struct Statistics {
  1: optional int64 null_count                 // NULL 值的数量
  2: optional int64 distinct_count             // 不同值的数量（通常不填充）
  3: optional binary max                       // 最大值（编码为二进制）
  4: optional binary min                       // 最小值（编码为二进制）
}
```

> **统计信息的精度**：Statistics 存在于 ColumnChunk 级别和 Page 级别（v2 通过 ColumnIndex）。它们用于谓词下推（Predicate Pushdown），允许 Reader 跳过不满足过滤条件的 Row Group 或 Page。

### 2.5 PageHeader（v2）

当 FileMetaData 的 `page_headers` 字段被填充（非必须的优化），或者每个 Page 前都内联了一个 PageHeader。

```thrift
struct PageHeader {
  1: required PageType type                     // DATA_PAGE / DATA_PAGE_V2 / DICTIONARY_PAGE / INDEX_PAGE
  2: required int32 uncompressed_page_size      // 页面未压缩大小
  3: required int32 compressed_page_size        // 页面压缩后大小
  4: optional int32 crc                         // v2，CRC32 校验和
  5: optional DataPageHeader data_page_header   // DATA_PAGE 的额外头部
  6: optional DataPageHeaderV2 data_page_header_v2  // DATA_PAGE_V2 的额外头部
  7: optional DictionaryPageHeader dictionary_page_header  // DICTIONARY_PAGE 额外头部
  8: optional IndexPageHeader index_page_header // INDEX_PAGE 额外头部
}
```

```thrift
struct DataPageHeader {
  1: required int32 num_values                  // 此页中的 value 数
  2: required Encoding encoding                 // 数据编码
  3: required Encoding definition_level_encoding // Definition Level 编码
  4: required Encoding repetition_level_encoding // Repetition Level 编码
  5: optional Statistics statistics             // Page 级别统计（v1）
}
```

**DATA_PAGE_V2**（v2 引入，更高效）：

```thrift
struct DataPageHeaderV2 {
  1: required int32 num_values                  // value 数
  2: required int32 num_nulls                   // NULL 数
  3: required int32 num_rows                    // 此页包含的行数
  4: required Encoding encoding                 // 数据编码
  5: required int32 definition_levels_byte_length  // Definition Level 数据的字节长度
  6: required int32 repetition_levels_byte_length  // Repetition Level 数据的字节长度
  7: optional bool is_compressed                // 是否已压缩（默认为 true）
  8: optional Statistics statistics             // Page 级别统计
}
```

**Page 类型枚举**：

```thrift
enum PageType {
  DATA_PAGE = 0,          // 数据页（V1 格式）
  INDEX_PAGE = 1,         // 索引页（当前标准未广泛使用）
  DICTIONARY_PAGE = 2,    // 字典页
  DATA_PAGE_V2 = 3,       // 数据页 V2（更紧凑的头部）
}
```

### 2.6 Thrift Compact Protocol 编码简析

Thrift Compact Protocol 采用变长整数和类型-字段 ID 合并编码：

| 编码技术 | 说明 | 示例 |
|---------|------|------|
| **Varint** | 每个字节的低 7 位为数据，最高位为延续标志 | int32 150 = 0x96 0x01 |
| **ZigZag** | 将有符号整数映射为无符号，小负数效率高 | -1 → 1, 1 → 2, -2 → 3 |
| **Field Delta** | 字段 ID 与前一个字段的差值编码 | 字段 1→3→4 编码为 1→2→1 |
| **Type-Id 合并** | TType 和 Field ID 编码在一个字节中 | 1 个 byte 携带类型和 ID 信息 |
| **String 长度前缀** | 字符串前跟 Varint 长度 + 原始数据 | "abc" → 0x03 + 0x61 0x62 0x63 |

> **典型 Footer 大小**：一个包含 1000 列、100 个 Row Group 的 Parquet 文件，Footer 大小通常在 100KB～500KB 之间。Footer 的大小直接影响读取时的初始 I/O 开销。

---

## 3. Row Group / Column Chunk / Page 三层结构

### 3.1 三层层次关系图

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Row Group 1                   num_rows=1000000, total_byte_size=512MB     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Column Chunk: "id" (INT64)                                         │  │
│  │  ├── data_page_offset: 0x00001000                                   │  │
│  │  ├── total_compressed_size: 8MB                                     │  │
│  │  ├── encodings: [PLAIN, RLE_DICTIONARY]                             │  │
│  │  ├── statistics: min=1, max=1000000, null_count=0                   │  │
│  │  └── Pages:                                                         │  │
│  │      ├── [Dictionary Page] @ 0x00001000  dict_size=1.2MB            │  │
│  │      ├── [Data Page V2]    @ 0x00013800  num_values=32768           │  │
│  │      ├── [Data Page V2]    @ 0x0002A000  num_values=32768           │  │
│  │      ├── ... (30 pages total)                                       │  │
│  │      └── [Data Page V2]    @ 0x008C0000  num_values=16960           │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Column Chunk: "name" (BYTE_ARRAY)                                  │  │
│  │  ├── data_page_offset: 0x008C4000                                   │  │
│  │  ├── statistics: min="Alice", max="Zoey"                            │  │
│  │  └── Pages: ...                                                     │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Column Chunk: "salary" (FLOAT)                                     │  │
│  │  └── Pages: ...                                                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────┐
│  Row Group 2                                                               │
│  ...                                                                       │
└────────────────────────────────────────────────────────────────────────────┘
```

**关键关系**：

| 层次 | 包含关系 | 1:N 方向 |
|------|---------|---------|
| File → Row Group | File 包含 1 个或多个 Row Group | 1:N |
| Row Group → Column Chunk | 一个 Row Group 包含所有列的 Chunk | 1:N（列数） |
| Column Chunk → Page | 一个 Column Chunk 包含多个 Page | 1:N |
| Page | 实际数据载体 | 原子单位 |

### 3.2 Row Group（行组）

**定义**：Row Group 是数据在行维度的逻辑分片，包含一定数量的完整行在所有列上的数据。

**特征**：

| 特征 | 值 |
|------|-----|
| **逻辑含义** | 行的水平分区，每个 Row Group 包含完整的行子集 |
| **典型大小** | 128MB ～ 1GB（未压缩），官方推荐 512MB ～ 1GB |
| **典型行数** | 数十万 ～ 数千万（取决于行宽） |
| **物理分布** | 列数据按列连续存储（列式），但 Row Group 之间在文件上顺序排列 |
| **独立性** | Row Group 之间完全独立，可并行读写 |

**Row Group 的设计目标**：
1. **并行性**：每个 Row Group 可以被独立地读取和处理
2. **I/O 粒度**：读取时可以跳过不相关的 Row Group（基于统计信息或列裁剪）
3. **内存控制**：单个 Row Group 的数据可以控制在合理的内存范围内

### 3.3 Column Chunk（列块）

**定义**：Column Chunk 是一个 Row Group 中某一列的数据在文件中的连续存储区域。

**特征**：

| 特征 | 值 |
|------|-----|
| **物理结构** | 文件中的连续字节区间 |
| **内部组成** | 多个 Page 的连续排列（Data Page + 可选的 Dictionary Page） |
| **编码独立** | 不同列可以使用不同的编码方式 |
| **压缩独立** | 不同列可以使用不同的压缩编解码器 |
| **统计信息** | 包含该列块中数据的 min / max / null_count |

**Column Chunk 的文件布局**：

```
┌─────────────────────────────────────────────────────┐
│  Column Chunk: "salary"                             │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  PageHeader (Thrift Compact)                │   │
│  │  type: DICTIONARY_PAGE                      │   │
│  │  uncompressed_size: 1000                    │   │
│  │  compressed_size: 800                       │   │
│  ├─────────────────────────────────────────────┤   │
│  │  Dictionary Page Data                       │   │
│  │  (已压缩/已编码的字典内容)                    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  PageHeader (Thrift Compact)                │   │
│  │  type: DATA_PAGE_V2                         │   │
│  │  num_values: 32768                          │   │
│  │  num_nulls: 234                             │   │
│  ├─────────────────────────────────────────────┤   │
│  │  Repetition Levels (RLE 编码)               │   │
│  │  Definition Levels (RLE 编码)               │   │
│  │  Data (RLE_DICTIONARY 编码)                 │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  PageHeader                                 │   │
│  │  type: DATA_PAGE_V2                         │   │
│  ├─────────────────────────────────────────────┤   │
│  │  Repetition Levels                          │   │
│  │  Definition Levels                          │   │
│  │  Data                                       │   │
│  └─────────────────────────────────────────────┘   │
│                      ...                            │
└─────────────────────────────────────────────────────┘
```

### 3.4 Page（页面）

Page 是 Parquet 中的最小 I/O 单元。共有三种主要的 Page 类型：

#### 3.4.1 Data Page（数据页）

两种版本：

**DATA_PAGE（v1）**：
```
┌─────────────────────────────────┐
│  PageHeader                     │
│  ├── type: DATA_PAGE           │
│  ├── uncompressed_page_size    │
│  ├── compressed_page_size      │
│  └── data_page_header:         │
│      ├── num_values            │
│      ├── encoding              │
│      ├── def_level_encoding    │
│      └── rep_level_encoding    │
├─────────────────────────────────┤
│  Page Data（压缩后）             │
│  ┌───────────────────────────┐  │
│  │ Repetition Levels         │  │
│  │ Definition Levels         │  │
│  │ Data Values               │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**DATA_PAGE_V2（v2）**：
```
┌─────────────────────────────────┐
│  PageHeader V2                  │
│  ├── type: DATA_PAGE_V2        │
│  ├── num_values                │
│  ├── num_nulls                 │
│  ├── num_rows                  │
│  ├── encoding                  │
│  ├── def_levels_byte_length    │
│  ├── rep_levels_byte_length    │
│  ├── is_compressed             │
│  └── statistics                │
├─────────────────────────────────┤
│  Repetition Levels（原始/RLE）   │
│  Definition Levels（原始/RLE）   │
├─────────────────────────────────┤
│  Data Values                     │
│  （如已压缩，则整个数据区域压缩）  │
└─────────────────────────────────┘
```

**V1 vs V2 的关键差异**：

| 特性 | DATA_PAGE (v1) | DATA_PAGE_V2 (v2) |
|------|---------------|-------------------|
| 头部大小 | 较大（需单独序列化 encoding） | 更紧凑 |
| Rep/Def Levels | 与数据一起整体压缩 | 独立于数据存储，不压缩 |
| NULL 计数 | 需扫描计算 | 直接提供 num_nulls |
| 行数 | 不直接提供 | 直接提供 num_rows |
| 校验和 | 无 | 可选 CRC32 |
| 统计信息 | 可选 | 可选 |

#### 3.4.2 Dictionary Page（字典页）

```
┌─────────────────────────────────┐
│  PageHeader                     │
│  ├── type: DICTIONARY_PAGE     │
│  ├── uncompressed_page_size    │
│  ├── compressed_page_size      │
│  └── dictionary_page_header:   │
│      ├── num_values            │
│      └── encoding (通常 PLAIN) │
├─────────────────────────────────┤
│  Dictionary Data（压缩后）       │
│  (key → index 的映射表)         │
└─────────────────────────────────┘
```

- 位于 Column Chunk 的**第一页**
- 包含该列所有唯一值的编码列表
- Data Page 中存储的是字典索引（整数），而非原始值
- `RLE_DICTIONARY` = `PLAIN` 编码的字典 + `RLE` 编码的索引

**典型流程**：
```
原始值: ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice"]
                          ↓
Dictionary: {0: "Alice", 1: "Bob", 2: "Charlie"}
                          ↓
Data Page (索引): [0, 1, 0, 2, 1, 0]
                          ↓
RLE 压缩: (0 出现 3 次 → 字面量或运行长度编码)
```

#### 3.4.3 Index Page（索引页）

当前标准中 INDEX_PAGE 类型虽已定义，但**实际实现中未广泛使用**。其设计目的是存储列的页级别索引信息，但在 v2 中通过 **OffsetIndex** 和 **ColumnIndex**（存储在 ColumnChunk 的元数据中）实现了类似功能。

### 3.5 v2 中的 OffsetIndex 和 ColumnIndex

v2 在 ColumnChunk 级别引入了两个辅助索引结构（存储在 ColumnChunk 元数据定义的偏移位置）：

```
┌────────────────────────────────────────────┐
│  OffsetIndex                               │
│  ┌──────────────────────────────────────┐  │
│  │  Page 0: offset=0x1000, size=8000    │  │
│  │  Page 1: offset=0x3000, size=7500    │  │
│  │  Page 2: offset=0x5000, size=8200    │  │
│  │  ...                                  │  │
│  └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│  ColumnIndex                               │
│  ┌──────────────────────────────────────┐  │
│  │  Page 0: min=10, max=99, null=0     │  │
│  │  Page 1: min=101, max=200, null=1   │  │
│  │  Page 2: min=202, max=300, null=0   │  │
│  │  ...                                  │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

**作用**：
- **OffsetIndex**：允许 Reader 直接定位到任一 Page 的起始位置，无需顺序扫描所有 PageHeader
- **ColumnIndex**：提供页级别的 min/max/null_count，用于更精细的谓词下推（跳过不满足条件的 Page）

### 3.6 各层级的元数据关联

```
FileMetaData
│
├── schema: [SchemaElement, ...]  ← 全局 Schema 定义
│
└── row_groups: [RowGroup, ...]   ← 所有 Row Group 的描述
    │
    ├── num_rows: int64            ← 此 Row Group 中的行数
    │
    └── columns: [ColumnChunk, ...]  ← 每列描述
        │
        ├── meta_data.file_path    ← 文件路径（多文件情况下）
        ├── meta_data.data_page_offset   ← 第一页偏移
        ├── meta_data.dictionary_page_offset  ← 字典页偏移
        ├── meta_data.statistics   ← 列块级别统计
        ├── meta_data.num_values   ← 列块中的总 value 数
        ├── offset_index_offset    → OffsetIndex（Page 级别偏移表）
        └── column_index_offset    → ColumnIndex（Page 级别统计）
            │
            └── PageHeader → Page Data
                ├── type: DATA_PAGE / DICTIONARY_PAGE
                ├── data_page_header.num_values  ← 页内 value 数
                ├── data_page_header.statistics  ← 页内统计
                └── crc: CRC32  ← v2 可选校验和
```

---

## 4. Dremel 编码原理

Dremel 编码由 Google 在 Dremel 论文中提出（2010），用于高效地编码和存储嵌套数据。其核心思想是利用 **Repetition Level（重复级别）**和 **Definition Level（定义级别）** 将树形嵌套数据打平为列式存储。

### 4.1 问题背景

考虑嵌套 schema：

```
message Document {
  required int64 DocId;
  optional group Links {
    repeated int64 Backward;
    repeated int64 Forward;
  }
  repeated group Name {
    repeated group Language {
      required string Code;
      optional string Country;
    }
    optional string Url;
  }
}
```

示例数据（一个 Document 实例）：

```
DocId: 10
Links: {Backward: [1, 2],  Forward: [5]}
Name: [
  {Language: [{Code: "en-us", Country: "us"}, {Code: "en"}],  Url: "http://A"},
  {Language: [{Code: "zh-cn", Country: "cn"}]}
]
```

问题：如何将这个树形结构转化为列式存储？

### 4.2 Repetition Level（重复级别，r）

**定义**：Repetition Level 表示当前值在哪个深度上**重复了其父路径**。

**核心含义**：当从当前值移动到下一个值时，Repetition Level 指明需要"向上回溯"的层数，以找到共享的祖先节点。

**规则**：
- **r = 0**：开始一个新记录（record boundary），表示前一个记录结束，新记录开始
- **r > 0**：该值属于同一记录的重复字段的又一个实例
- **对于 `required` 和 `optional` 字段**：r 始终为 0（它们不会重复）

**计算方式**（从树到列的转换过程）：
1. 按先序遍历这棵数据树
2. 对于每个叶子节点的值，检查它和上一个叶子值共享的最大父路径深度
3. 共享深度 = 从根开始、路径完全相同的节点数
4. 共享深度对应的字段如果是 `repeated` 的，则 r = 该 repeated 字段的深度；否则 r = 0

#### 示例计算

以上面的数据为例，列 `Name.Language.Code` 的值序列：

```
值序列: ["en-us", "en", "zh-cn"]
```

**从 "en-us" → "en"**：
- "en-us" 的路径：`Document.Name[0].Language[0].Code`
- "en" 的路径：`Document.Name[0].Language[1].Code`
- 共享路径：`Document.Name[0].Language`（到 Language 级别）
- Language 是 `repeated` 的
- `Language` 在路径中的深度 = 3（Document->Name->Language，从 0 计数为 2）
- 但规范要求 r 的计数只包括 `repeated` 字段的重复层次
- 在 Name.Language.Code 这条路径中，repeated 字段：Name (depth 1), Language (depth 2)
- 共享到 Language，所以 r = 2

等一下，让我更准确地计算。

实际上 Dremel 论文中的 r 定义是：**路径中共享的 repeated 字段的数量**。

路径：`root.Document.Name.Language.Code`
- Document: message, 不计入
- Name: repeated (深度 1)
- Language: repeated (深度 2)
- Code: required/leaf

**从 "en-us" 到 "en"**：
- "en-us" 完整路径：`Document.Name[0].Language[0].Code`
- "en" 完整路径：`Document.Name[0].Language[1].Code`
- 共享前缀：`Document.Name[0]` 之后，Language 的索引从 0 变为 1
- 共享的 repeated 字段：Name（因为 Name[0] 是共享的）
- Language 也变了索引，所以不共享
- 所以 r = Name 在 repeated 字段序列中的位置 = 1

等等，让我再看看。

Dremel 论文原文：The repetition level is the level at which the repeated field in the field path repeated. For r = 0 it means a new record starts.

更准确地说：r 的计算是从根到叶子的路径中，当从上一个值移动到当前值时，需要"重新开始"的 repeated 字段的最深层次。

路径中 repeated 字段的索引（0-based）：
- Document（message）→ 不是 repeated
- Name（repeated）→ 索引 0
- Language（repeated）→ 索引 1
- Code（leaf）

从 "en-us" (Name[0].Language[0]) 到 "en" (Name[0].Language[1])：
- Name 的索引保持 0（同一个 Name 对象内）
- Language 的索引从 0 变为 1
- 所以最深的不变的 repeated 字段是 Name → r = 0 (Name 的索引)

不对，让我重新理一下。Dremel 论文中的定义是：

The repetition level is the field definition level (depth in the record definition tree) of the repeated field that repeated.

路径深度计数方式（从 1 开始）：
- Document: depth 1
- Name: depth 2 (repeated)
- Language: depth 3 (repeated)
- Code: depth 4

从 "en-us" 到 "en"：
两者在 Document.Name 级别共享
Name 是 repeated，Language 是 repeated
Language 变了，Name 没变
所以 r = depth of Name = 2

从 "en" 到 "zh-cn"：
- "en" 路径：Document.Name[0].Language[1]
- "zh-cn" 路径：Document.Name[1].Language[0]
- 共享：只有 Document
- Document 不是 repeated
- 所以 r = 0（新记录或者说最外层）

从第一个值 "en-us" 开始的 r = 0（总是 0，表示这是新记录的首次出现）。

所以：
```
"en-us": r=0
"en":    r=2
"zh-cn": r=0
```

再算一下 Name.Url 列：
值序列：["http://A", null]（Name[1].Url 不存在）

从 "http://A" → null（即 Name[0].Url → Name[1].Url 不存在）：
- 共享路径：Document
- Name 从索引 0 变为 1
- 没有 shared repeated 字段
- r = 0

```
"http://A": r=0
null:       r=0
```

实际上，对于 Url 列，第二个值没有出现在原始数据中，所以只输出非空的值。

- Url[0] = "http://A" (r=0)
- Url[1] = 不存在

所以 Name.Url 列只有一个值：r=0, "http://A"

不，实际上 Dremel 编码会为每个可能的叶子值都产生输出。如果值为 null，definition level 会表明 null。

让我重新看看。

在 Dremel 中，叶子值的生成规则是按并行深度优先遍历。对于每个叶子字段，产生的记录是：

Name.Language.Code:
1. r=0, d=2, "en-us"
   (Name[0].Language[0].Code = "en-us")
2. r=2, d=2, "en"
   (Name[0].Language[1].Code = "en")
3. r=0, d=2, "zh-cn"
   (Name[1].Language[0].Code = "zh-cn")

Name.Language.Country:
1. r=0, d=3, "us"
   (Name[0].Language[0].Country = "us")
2. r=2, d=2, null
   (Name[0].Language[1].Country 不存在，d=2 表示 Language 存在但 Country 不存在)
3. r=0, d=3, "cn"
   (Name[1].Language[0].Country = "cn")

Name.Url:
1. r=0, d=1, "http://A"
   (Name[0].Url = "http://A")
2. r=0, d=0, null
   (Name[1].Url 不存在，d=0 表示 Name 存在但 Url 不存在)

Links.Backward:
1. r=0, d=2, 1
2. r=1, d=2, 2
   (Backward[0]→Backward[1] 在 Links 级别重复)

Links.Forward:
1. r=0, d=2, 5

### 4.3 Definition Level（定义级别，d）

**定义**：Definition Level 表示从根到当前值的路径中有多少 **optional** 或 **repeated** 字段是实际存在的。

**核心含义**：d 用于区分"值是 null（因为父字段不存在）"和"值就是 null"。

**规则**：
- d = 路径中 optional/repeated 字段的总数：该值完全存在
- d < 路径中 optional/repeated 字段的总数：某个祖先字段缺失，导致此值不存在
- d = 路径中 repeated 字段数（不计算 optional）：该字段本身被设置了但值不存在（对于 optional 字段）

**计算方式**：
路径中所有定义为 `optional` 或 `repeated` 的字段组成 definition path。d 的值等于实际存在的路径长度。

#### 示例计算

列 `Name.Language.Code`：
- 路径中的 optional/repeated 字段：Name (repeated, d=1), Language (repeated, d=2), Code (required, 不计)
- 最大 d = 2
- 如果 Code 存在，d=2
- 如果 Language 存在但 Code 不存在：不可能，因为 Code 是 required
- 如果 Name 存在但 Language 不存在：d=1
- 如果 Name 不存在：d=0

列 `Name.Language.Country`：
- 路径中的 optional/repeated 字段：Name (rep), Language (rep), Country (opt)
- 最大 d = 3
- d=3: Country 存在
- d=2: Language 存在但 Country 不存在（optional 字段为 null）
- d=1: Name 存在但 Language 不存在
- d=0: Name 不存在

列 `Name.Url`：
- 路径中的 optional/repeated 字段：Name (rep), Url (opt)
- 最大 d = 2
- d=2: Url 存在
- d=1: Name 存在但 Url 不存在（optional 字段为 null）
- d=0: Name 不存在

### 4.4 完整列编码结果

对于示例数据，各列的 (r, d, value) 三元组序列：

**Links.Backward**（repeated int64）：

| # | r | d | value | 说明 |
|---|----|----|-------|------|
| 1 | 0 | 2 | 1 | Links[0].Backward[0] = 1 |
| 2 | 1 | 2 | 2 | Links[0].Backward[1] = 2 |

**Links.Forward**（repeated int64）：

| # | r | d | value | 说明 |
|---|----|----|-------|------|
| 1 | 0 | 2 | 5 | Links[0].Forward[0] = 5 |

**Name.Language.Code**（repeated required string）：

| # | r | d | value | 说明 |
|---|----|----|-------|------|
| 1 | 0 | 2 | "en-us" | Name[0].Language[0].Code |
| 2 | 2 | 2 | "en" | Name[0].Language[1].Code |
| 3 | 0 | 2 | "zh-cn" | Name[1].Language[0].Code |

**Name.Language.Country**（repeated optional string）：

| # | r | d | value | 说明 |
|---|----|----|-------|------|
| 1 | 0 | 3 | "us" | Name[0].Language[0].Country = "us" |
| 2 | 2 | 2 | null | Name[0].Language[1].Country does not exist |
| 3 | 0 | 3 | "cn" | Name[1].Language[0].Country = "cn" |

**Name.Url**（optional string）：

| # | r | d | value | 说明 |
|---|----|----|-------|------|
| 1 | 0 | 1 | "http://A" | Name[0].Url = "http://A" |
| 2 | 0 | 0 | null | Name[1] does not have Url |

### 4.5 Dremel 编码的二进制格式

r 和 d 都是整数，通过 **RLE（Run-Length Encoding）** 或 **BIT-PACKED** 编码存储：

```
Page Layout for Rep/Def Levels:

┌──────────────────────────────────────────────┐
│  RLE/Bit-Packing Hybrid Encoding             │
│                                              │
│  数据流由头字节标记区域：                       │
│                                              │
│  Header byte (低 1 位 = 编码类型)              │
│  ├── bit0 = 0: 接下来是 RLE 编码              │
│  │   剩余 7 位 = 游程长度（通过 varint 扩展）    │
│  │   后续字节 = 重复的值                       │
│  └── bit0 = 1: 接下来是 BIT-PACKED 编码        │
│      剩余 7 位 = 打包的组数                     │
│      后续字节 = 每组 8 个值的位打包             │
│                                              │
│  RLE 示例（max_bit_width=2）:                  │
│  值序列: [0, 0, 0, 1, 1, 2, 2, 2, 3]        │
│  → (0×3, 1×2, 2×3, 3×1)                     │
│  → 编码: [0x03<<1|0=6, 00]  [0x02<<1=4, 01]  │
│          [0x03<<1=6, 10]  [0x01<<1=2, 11]    │
└──────────────────────────────────────────────┘
```

**最大位宽计算**：

对于 r：最大位宽 = `ceil(log2(max_repetition_level + 1))`
- 如果 schema 没有 repeated 字段，r 始终为 0 → 位宽 = 0（不占用空间）
- 对于上面的例子，r 最大值为 2 → 位宽 = 2

对于 d：最大位宽 = `ceil(log2(max_definition_level + 1))`
- 对于 Name.Language.Code，d 最大为 2 → 位宽 = 2
- 对于 Name.Language.Country，d 最大为 3 → 位宽 = 2

### 4.6 从 Dremel 编码重建记录

重建算法：
1. 并行遍历所有叶子列的 (r, d, value) 序列
2. 当 r = 0 时，开始一个新记录
3. 根据 r 的值决定在哪个 repeated 级别上创建新的重复实例
4. 根据 d 的值决定路径上每个 optional/repeated 字段的存在性

对于 r 的处理：
- r = 0：顶层已变，完全跳回到根节点，所有字段重新开始
- r = 2：在 depth=2 的 repeated 字段上创建新实例（Language）

对于 d 的处理：
- d = max：值存在，将值写入对应位置
- d < max 但 d > 0：对应深度的字段不存在，设置为 null
- d = 0：根级 optional/repeated 就不存在，整条路径为 null

---

## 5. 完整读写生命周期

### 5.1 写入流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          写入流程（Write Path）                              │
└─────────────────────────────────────────────────────────────────────────────┘

 输入数据（行式，如 Arrow RecordBatch / Avro / CSV）
        │
        ▼
┌──────────────────┐
│  1. Schema 构建   │
│  ┌──────────────┐│
│  │ 解析输入 Schema││
│  │ 构建 SchemaTree││
│  │ 分配 field_id  ││
│  │ 确定物理类型    ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. 列数据分解    │
│  (Columnarizing) │
│  ┌──────────────┐│
│  │ 行→列转置    ││
│  │ 计算 r/d     ││
│  │ ← Dremel     ││
│  │   Encoding   ││
│  │ 按列收集数据  ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. 编码(Encode) │
│  ┌──────────────┐│
│  │ 选择编码方案  ││
│  │ ← PLAIN      ││
│  │ ← RLE_DICT   ││
│  │ ← DELTA_BP   ││
│  │ ← DELTA_LEN  ││
│  │ 编码 r/d     ││
│  │ 编码数据值    ││
│  │ (可能建字典)  ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. 压缩         │
│  (Compress)      │
│  ┌──────────────┐│
│  │ 可逐列配置    ││
│  │ ← Snappy     ││
│  │ ← Gzip       ││
│  │ ← Zstd       ││
│  │ ← LZ4_RAW    ││
│  │ 或跳过压缩    ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. Page 组装    │
│  (Page Assembly) │
│  ┌──────────────┐│
│  │ 切分 Page     ││
│  │ ← 目标大小    ││
│  │ (通常 1MB)   ││
│  │ 写 PageHeader ││
│  │ 写校验和(CRC) ││
│  │ 可选建索引    ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  6. Column       │
│     Chunk 组装   │
│  ┌──────────────┐│
│  │ 收集该列的    ││
│  │ 所有 Page    ││
│  │ 记录统计信息  ││
│  │ (min/max/    ││
│  │  null_count) ││
│  │ 写 OffsetIdx ││
│  │ 写 ColumnIdx ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  7. Row Group    │
│     组装         │
│  ┌──────────────┐│
│  │ 收集所有列    ││
│  │ 的 Chunk     ││
│  │ 写 Column    ││
│  │ Chunk 元数据 ││
│  │ 统计 Row Gp  ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼（重复步骤 2-7 直到所有数据写入）
         │
         ▼
┌──────────────────┐
│  8. Footer 写入  │
│  ┌──────────────┐│
│  │ 序列化        ││
│  │ FileMetaData ││
│  │ (Thrift      ││
│  │  Compact)    ││
│  │ 写入元数据    ││
│  │ 写入长度(4B) ││
│  │ 写入 PAR1    ││
│  └──────────────┘│
└──────────────────┘
```

#### 5.1.1 写入流程详细说明

**阶段 1 - Schema 构建**：
1. 输入数据通常具有自描述 schema（如 Arrow Schema 或 Avro Schema）
2. Writer 将逻辑类型映射为 Parquet 物理类型（如 `String → BYTE_ARRAY`、`Decimal(10,2) → FIXED_LEN_BYTE_ARRAY`）
3. 构建 Schema 树的先序遍历列表
4. 为每个叶子节点确定编码方式和压缩方式（可逐列配置）

**阶段 2 - 列数据分解**：
1. 将行式数据逐列拆分
2. 对于嵌套数据，同时计算 Definition Level 和 Repetition Level
3. 每列数据被组织为 `(r, d, value)` 三元组流
4. 此阶段是写入路径中最消耗 CPU 的部分之一（需要内存中的行→列转置）

**阶段 3 - 编码**：
1. 为每列选择最佳编码策略（通常基于数据类型和基数估算）
2. 常见编码：
   - `PLAIN`：原始值直接存储（适合基数高的列）
   - `RLE_DICTIONARY`：建字典后存储整数索引（适合基数低的列）
   - `DELTA_BINARY_PACKED`：增量编码（适合有序数值列）
   - `DELTA_LENGTH_BYTE_ARRAY`：变长前缀编码（适合字符串列）
   - `BYTE_STREAM_SPLIT`：按字节平面拆分（适合浮点数列，v2）
3. r 和 d 使用 RLE/BIT-PACKED HYBRID 编码

**阶段 4 - 压缩**（可选）：
1. 使用列级别配置的压缩算法（Snappy、Gzip、Zstd 等）
2. 通常 `compressed_size < uncompressed_size`
3. 在 V2 中，r 和 d 不压缩，只压缩数据值部分

**阶段 5 - Page 组装**：
1. 将编码和压缩后的数据切分为固定大小的 Page（典型 1MB）
2. 每个 Page 前写入 PageHeader（Thrift Compact 序列化）
3. 适当时写入校验和（CRC32）

**阶段 6 - Column Chunk 组装**：
1. 收集该列的所有 Page
2. 计算 ColumnChunk 级别的统计信息（min/max/null_count）
3. 如使用 v2，在 Chunk 末尾写入 OffsetIndex 和 ColumnIndex

**阶段 7 - Row Group 组装**：
1. 收集一个 Row Group 中所有列的 Chunk
2. 行数对齐：每个 Column Chunk 中的值数应一致

**阶段 8 - Footer 写入**：
1. 构造 FileMetaData（Thrift 对象）
2. 用 Compact Protocol 序列化
3. 写入 4 字节的元数据长度（little-endian int32）
4. 写入 4 字节的 `PAR1` 签名

### 5.2 读取流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          读取流程（Read Path）                               │
└─────────────────────────────────────────────────────────────────────────────┘

 Parquet 文件
        │
        ▼
┌──────────────────┐
│  1. Footer 读取  │
│  ┌──────────────┐│
│  │ 尾 8 字节:    ││
│  │ PAR1 + 长度  ││
│  │ ← 判定有效    ││
│  │ ← 读元数据    ││
│  │ ← Thrift     ││
│  │   Compact    ││
│  │   反序列化    ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. 元数据解析   │
│  ┌──────────────┐│
│  │ 解析 Schema  ││
│  │ 解析列路径   ││
│  │ 读统计信息   ││
│  │ 定位 RGs     ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  3. Row Group 裁剪           │
│  (Row Group Pruning)         │
│  ┌──────────────────────────┐│
│  │ 对每个 RG 判断是否需要   ││
│  │                          ││
│  │ ← 列裁剪: 只读需要的列  ││
│  │                          ││
│  │ ← 谓词下推:              ││
│  │   RG.min ≤ filter.val   ││
│  │   RG.max ≥ filter.val   ││
│  │   (跳过多余 RG)          ││
│  │                          ││
│  │ ← 行数限制: LIMIT/OFFSET ││
│  └──────────────────────────┘│
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  4. Column Chunk 定位        │
│  ┌──────────────────────────┐│
│  │ 对选中的 RG 中的每列:    ││
│  │ ← 定位 Chunk 偏移        ││
│  │ ← 读 OffsetIndex        ││
│  │ ← 读 ColumnIndex        ││
│  │ ← Page 级别裁剪:         ││
│  │   跳过不满足条件的 Page  ││
│  └──────────────────────────┘│
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────┐
│  5. Page 加载    │
│  ┌──────────────┐│
│  │ 定位 Page     ││
│  │ 偏移 + 大小  ││
│  │ ← 随机读     ││
│  │    (pread)   ││
│  │ 或批量顺序读  ││
│  │ 验证 CRC32   ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  6. 解压         │
│  (Decompress)    │
│  ┌──────────────┐│
│  │ 根据 codec    ││
│  │ 解压数据区    ││
│  │ ← Snappy     ││
│  │ ← Gzip       ││
│  │ ← Zstd       ││
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  7. 解码 (Decode)            │
│  ┌──────────────────────────┐│
│  │ 解码 r/d → 重建记录结构  ││
│  │                          ││
│  │ ← 数据解码:              ││
│  │   PLAIN → 直接读         ││
│  │   Dict → 查字典          ││
│  │   Delta → 累加恢复       ││
│  │   ByteSplit → 拼接       ││
│  └──────────────────────────┘│
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  8. 结果组装                  │
│  ┌──────────────────────────┐│
│  │ 列→行转置               ││
│  │ 用 r/d 重建嵌套结构     ││
│  │ ← Dremel 逆变换         ││
│  │ 产出行式结果             ││
│  │ (Arrow / 内存行)        ││
│  └──────────────────────────┘│
└──────────────────────────────┘
```

#### 5.2.1 读取流程详细说明

**阶段 1 - Footer 读取**：
1. 打开文件，执行 `lseek(file, file_size - 8, SEEK_SET)`（2 次 I/O）
2. 读取尾部 4 字节验证 magic
3. 读取前 4 字节得元数据长度 N
4. 执行第二次 `lseek(file, file_size - 8 - N, SEEK_SET)` 读取完整的 FileMetaData
5. Thrift Compact 反序列化

**阶段 2 - 元数据解析**：
1. 解析 Schema 树，确定需要读取的列及其路径
2. 遍历 Row Group 列表，获取每个 RG 的行数、大小、各列的统计信息

**阶段 3 - Row Group 裁剪**：
1. **列裁剪（Column Pruning）**：只读取 SELECT 语句中涉及的列对应的 Column Chunk
2. **谓词下推（Predicate Pushdown）**：利用 min/max 统计信息跳过不满足 WHERE 条件的 Row Group
3. **分区裁剪**：对于分区的字段，直接跳过不相关的分区对应的 Row Groups

**阶段 4 - Column Chunk 定位**：
1. 对每个选中的 Column Chunk，从元数据中获取 `data_page_offset`
2. 如果使用 v2，读取 OffsetIndex 获取各 Page 的精确偏移
3. 利用 ColumnIndex 进行 Page 级别裁剪（对谓词进行更精细的过滤）

**阶段 5 - Page 加载**：
1. 根据要读取的 Page 列表，计算连续区域进行批量读取（减少 I/O 次数）
2. 对每个 Page 验证 CRC32 校验和（如果存在）
3. 将 Page 数据读入内存缓冲区

**阶段 6 - 解压**：
1. 使用 PageHeader 中指定的 codec 解压数据
2. V2 中 r 和 d 不压缩，直接读取

**阶段 7 - 解码**：
1. 分别解码 Repetition Levels、Definition Levels 和数据值
2. 字典编码的列需要进行字典查找
3. 增量编码的列需要累加恢复原始值

**阶段 8 - 结果组装**：
1. 利用 r 和 d 重建原始记录结构（Dremel 解码）
2. 列到行的转置
3. 最终产出行式结果（通常以 Arrow RecordBatch 或行列表形式返回）

### 5.3 读写流程对比

| 阶段 | 写入 | 读取 |
|------|------|------|
| Schema | 从输入 Schema 构建 Parquet Schema | 从 Footer 解析 Schema |
| 数据布局 | 行→列转置 | 列→行转置 |
| r/d | 从嵌套数据计算 r/d | 从 r/d 重建嵌套数据 |
| 编码 | 原始值→编码字节 | 编码字节→原始值 |
| 压缩 | 压缩编码后数据 | 解压还原编码数据 |
| I/O | 顺序写，写一次 | 随机读（可能需要跳读），读特定 Page |
| 元数据 | 最后写入 Footer | 最先读取 Footer |
| 并行度 | 按 Row Group 分块并行 | 按 Row Group 分块并行 + Page 级别 |

---

## 6. 参考资料

### 官方规范

| 资源 | 链接 |
|------|------|
| Apache Parquet 格式官方文档 | https://parquet.apache.org/docs/file-format/ |
| Parquet 格式规范（GitHub） | https://github.com/apache/parquet-format |
| Thrift Compact Protocol 规范 | https://github.com/apache/thrift/blob/master/doc/specs/thrift-compact-protocol.md |

### 核心论文

| 论文 | 说明 |
|------|------|
| *Dremel: Interactive Analysis of Web-Scale Datasets* (VLDB 2010) | 提出 Dremel 嵌套列式存储和 r/d 编码 |
| *Parquet: Columnar Storage for the People* (VLDB 2013) | Parquet 的设计理念和架构概述 |

### 参考实现

| 项目 | 语言 | 链接 |
|------|------|------|
| parquet-mr（官方 Java 实现） | Java | https://github.com/apache/parquet-mr |
| parquet-cpp / Apache Arrow | C++ | https://github.com/apache/arrow/tree/main/cpp/src/parquet |
| parquet-python / PyArrow | Python | https://github.com/apache/arrow/tree/main/python/pyarrow/parquet |
| parquet-rs | Rust | https://github.com/apache/arrow-rs/tree/master/parquet |

### 附加阅读

- *Dremel 论文中文深度解析*：https://storage.googleapis.com/pub-tools-public-publication-data/pdf/36632.pdf
- Apache Arrow 对 Parquet 的读写实现文档
- 《The Internals of Parquet》- Understanding Parquet's Metadata and Page Layout

---

> **文档信息**：本文档为 T0151 调研子任务的产出，隶属于父任务 T0150（Parquet 格式深度技术调研）。技术细节基于 Parquet Format v2.x 规范，参考了 Apache Parquet 官方文档及 Dremel 论文。
