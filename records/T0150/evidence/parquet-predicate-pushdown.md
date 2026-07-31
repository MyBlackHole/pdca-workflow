# Parquet 谓词下推（Predicate Pushdown）原理调研

## 调研目标

深入理解 Apache Parquet 格式中谓词下推的技术原理，覆盖统计信息组织、Row Group 裁剪、Page Index 机制、Bloom Filter，以及与主流查询引擎的集成方式。

---

## 第一部分：统计信息组织

### 1.1 Parquet 文件整体布局

```
┌─────────────────────────────────┐
│  Magic Number "PAR1"            │  ← 4 bytes
├─────────────────────────────────┤
│  Row Group 0                    │
│  ├─ Column Chunk 0 (col_a)     │
│  │  ├─ Page 0 (Data Page)      │
│  │  ├─ Page 1 (Data Page)      │
│  │  └─ Page 2 (Dictionary Page)│
│  ├─ Column Chunk 1 (col_b)     │
│  └─ ...                        │
├─────────────────────────────────┤
│  Row Group 1                    │
│  ...                            │
├─────────────────────────────────┤
│  Footer                         │
│  ├─ FileMetaData               │
│  │  ├─ schema                  │
│  │  ├─ num_rows                │
│  │  ├─ RowGroup[0..N]          │
│  │  │  ├─ ColumnChunk[0..M]   │
│  │  │  │  ├─ meta_data        │  ← statistics (Parquet 1.0)
│  │  │  │  ├─ column_index_ref │  ← ColumnIndex offset (Parquet 2.0+)
│  │  │  │  └─ offset_index_ref │  ← OffsetIndex offset (Parquet 2.0+)
│  │  └─ column_indexes /        │
│  │      offset_indexes         │
│  └─ Footer length (4 bytes)    │
├─────────────────────────────────┤
│  Magic Number "PAR1"            │  ← 4 bytes
└─────────────────────────────────┘
```

### 1.2 ColumnIndex（列索引）

ColumnIndex 是 Parquet 2.0+（格式版本 >= 2）引入的结构，存储在 Footer 之后。每个 ColumnChunk 对应一个 ColumnIndex，包含该列每个 Page 的统计信息。

**Thrift 定义（parquet.thrift）：**

```thrift
struct ColumnIndex {
  /** 每个 Page 的 null_count，空页用 -1 填充 */
  1: required list<i64> null_pages
  /** 每个 Page 的最小值（字节数组，需反序列化为实际类型） */
  2: required list<binary> min_values
  /** 每个 Page 的最大值（字节数组，需反序列化为实际类型） */
  3: required list<binary> max_values
  /** 本列是否有 NULL 值 */
  4: required i64 boundary_order
  /** 每个 Page 中非 NULL 值的数量 */
  5: optional list<i64> null_counts
}

struct OffsetIndex {
  /** 每个 Page 在文件中的偏移量 */
  1: required list<i64> page_locations
  /** 每个 Page 的压缩后大小 */
  2: required list<i32> compressed_page_sizes
  /** 每个 Page 的第一行索引（全局行号） */
  3: required list<i64> first_row_index
  /** 每个 Page 最后一行索引（行号偏移替代方案） */
  4: optional list<i64> last_row_index
  /** 每个 Page 未压缩大小 */
  5: optional list<i32> uncompressed_page_sizes
}
```

**写入流程：**

```
Writer 写入数据
  → 在 DataPage 生成时记录 min/max/null_count
  → 一个 ColumnChunk 完成后，收集所有 Page 的统计
  → 构造 ColumnIndex + OffsetIndex
  → 追加到文件末尾（Footer 之后）
  → 在 ColumnChunk.meta_data 中记录对应的 offset/length
```

**读取流程：**

```
Reader 读 Footer
  → 解析 FileMetaData 获取 ColumnChunk 元数据
  → 通过 column_index_offset / column_index_length 定位 ColumnIndex
  → 通过 offset_index_offset / offset_index_length 定位 OffsetIndex
  → 逐 Page 比较 min/max 决定哪些 Page 需读取
```

### 1.3 OffsetIndex（偏移索引）

OffsetIndex 与 ColumnIndex 配套使用，定位每个 Page 在文件中的物理位置。

**存储位置关系（Parquet 2.0+）：**

```
File Layout (with ColumnIndex/OffsetIndex)
┌─────────────────────────────┐
│  Data Pages                 │  ← Row Group 数据
├─────────────────────────────┤
│  Footer                     │
│  ├─ FileMetaData            │
│  │  ├─ RowGroup[0]          │
│  │  │  ├─ ColumnChunk[0]    │
│  │  │  │  ├─ meta_data      │
│  │  │  │  │  ├─ column_index_offset  │  → 指向 ColumnIndex
│  │  │  │  │  └─ offset_index_offset  │  → 指向 OffsetIndex
│  │  │  │  └─ ...            │
│  │  └─ ...                  │
│  └─ Footer length            │
├─────────────────────────────┤
│  ColumnIndex[0]              │  ← Parquet 2.0+ 扩展
│  │  null_pages: [0,0,1,0]   │
│  │  min_values: [1,5,~,10]  │
│  │  max_values: [4,9,~,15]  │
│  ├─ ColumnIndex[1]           │
│  └─ ...                     │
├─────────────────────────────┤
│  OffsetIndex[0]              │  ← 每个 ColumnChunk 的 Page 位置
│  │  page_locations: [0,100] │
│  │  compressed_sizes: [100]│
│  │  first_row_index: [0]   │
│  └─ ...                     │
└─────────────────────────────┘
```

### 1.4 统计信息的级别对比

| 级别 | 存储位置 | 粒度 | 支持版本 | I/O 开销 |
|------|---------|------|---------|---------|
| File Meta | Footer schema | 整个文件 | 1.0+ | 极小（Footer 常驻内存） |
| Row Group | ColumnChunk.meta_data.statistics | Row Group | 1.0+ | 极小（Footer 常驻内存） |
| Page (ColumnIndex) | Footer 后独立区域 | 单个 Page | 2.0+ | 中等（需读取 ColumnIndex 区域） |
| Bloom Filter | 列数据后独立区域 | 列级别 | 2.0+ | 小（Bloom Filter 过滤） |

---

## 第二部分：Row Group 裁剪（Row Group Pruning）

### 2.1 原理

Row Group 是 Parquet 中数据水平分区的逻辑单元（通常包含 1M+ 行）。每个 ColumnChunk 在其 `meta_data.statistics` 中记录了该列在行组内的 min/max/null_count。查询引擎利用这些统计信息，在读取数据前即可跳过不满足 WHERE 条件的 Row Group。

**Parquet 1.0 statistics 的 Thrift 定义：**

```thrift
struct Statistics {
  1: optional i64 max              // 已废弃，使用 max_value
  2: optional i64 min              // 已废弃，使用 min_value
  3: optional i64 null_count
  4: optional i64 distinct_count
  5: optional binary max_value     // Parquet 2.0+ 明确类型
  6: optional binary min_value     // Parquet 2.0+ 明确类型
}
```

### 2.2 示例

```
Parquet File
├── Row Group 0 (rows 0-999999)
│   ├── id: statistics { min: 1, max: 5000, null_count: 0 }
│   └── name: statistics { min: "A", max: "M", null_count: 10 }
├── Row Group 1 (rows 1000000-1999999)
│   ├── id: statistics { min: 5001, max: 15000, null_count: 0 }
│   └── name: statistics { min: "N", max: "Z", null_count: 5 }
└── Row Group 2 (rows 2000000-2999999)
    ├── id: statistics { min: 15001, max: 30000, null_count: 0 }
    └── name: statistics { min: "A", max: "Z", null_count: 0 }

查询: SELECT * FROM t WHERE id > 10000

裁剪结果:
  Row Group 0: min=1, max=5000 → 全部不满足 → ❌ 跳过
  Row Group 1: min=5001, max=15000 → 部分满足 → ✅ 读取
  Row Group 2: min=15001, max=30000 → 全部满足 → ✅ 读取

=> 跳过 33% 的 Row Group，减少约 33% I/O
```

### 2.3 优势与局限

| 方面 | 说明 |
|------|------|
| 优势 | 宏观裁剪效果最显著，跳过整个 Row Group 可完全避免 I/O |
| 局限 | 粒度粗，Row Group 很大时裁剪精度低 |
| 条件 | 依赖数据排序——列数据越有序，min/max 范围越窄，裁剪效果越好 |
| 适用 | 范围查询（>、<、BETWEEN）效果最好 |
| 局限 | 对等值查询（WHERE id = 123）效果差，除非数据高度排序 |

### 2.4 多列协同裁剪

引擎可同时利用多个谓词进行复合裁剪：

```
查询: SELECT * FROM t WHERE id > 5000 AND date > '2024-01-01'

Row Group 0:
  id:   [1, 5000]   → id > 5000 不满足 → 跳过
  date: [2023-06, 2024-06] → 即使 date 满足，id 已跳过
结论: 跳过

Row Group 1:
  id:   [5001, 15000] → id 部分满足
  date: [2024-03, 2024-09] → date 满足
结论: 读取
```

---

## 第三部分：Page Index 机制（Parquet 2.0+）

### 3.1 Page 级别统计

Page 是 Parquet 中数据存储的最小容器（通常 1MB 左右）。Parquet 2.0+ 的 ColumnIndex 为每个 Page 独立维护 min/max 统计，提供了比 Row Group 裁剪更精细的过滤能力。

### 3.2 与 Row Group 裁剪的协同工作

```
┌─────────────────────────────────────────────────────────┐
│                 谓词下推执行流                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SQL: SELECT * FROM t WHERE age BETWEEN 20 AND 30       │
│                                                         │
│  Step 1: Row Group Pruning (Footer statistics)          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ RG0: age [1, 100]  → 需读取                       │  │
│  │ RG1: age [50, 80]  → 不满足 20-30 → ❌ 跳过       │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                               │
│  Step 2: Page Index Pruning (ColumnIndex)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ RG0, col=age, 读取 ColumnIndex                    │  │
│  │   Page 0: [1, 15]   → ❌ 跳过                     │  │
│  │   Page 1: [16, 25]  → ✅ 读取                     │  │
│  │   Page 2: [24, 35]  → ✅ 读取                     │  │
│  │   Page 3: [36, 100] → ❌ 跳过                     │  │
│  │ Result: 读取 2/4 个 Page，减少 50% 数据读取量     │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                               │
│  Step 3: 读取命中的 Page 数据 + 逐行过滤                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.3 存储位置与加载方式

```
Footer 解析阶段（零额外 I/O）：
  Footer 中的 ColumnChunk.meta_data.statistics
  → 用于 Row Group 裁剪
  → 完全在内存中完成

第一次数据读取前（额外 I/O）：
  ColumnIndex 存储在 Footer 后的单独区域
  → 只有 Row Group 裁剪通过后，才读取 ColumnIndex
  → 只读需要列对应的 ColumnIndex（不会全读）
  → 延迟加载（Lazy Loading）

Page 数据读取：
  OffsetIndex 提供 Page 物理位置
  → 跳过不满足的 Page，只 seek 到需要 Page 的 offset
  → 随机读（Random Read），减少 I/O 量
```

### 3.4 数据排序对 Page Index 效果的影响

```
有序数据（Sorted）：
  Page 0: [1, 10]    min=1,  max=10
  Page 1: [11, 20]   min=11, max=20
  Page 2: [21, 30]   min=21, max=30
  查询 age=15: 仅需读取 Page 1 → 裁剪率 66%

无序数据（Unsorted）：
  Page 0: [1, 100]   min=1,  max=100
  Page 1: [10, 90]   min=10, max=90
  Page 2: [5, 95]    min=5,  max=95
  查询 age=15: 所有 Page 都覆盖 15 → 裁剪率 0%
```

**结论：** Page Index 在按列排序（clustering/sorting）的数据上效果最佳。建议在写入 Parquet 时按查询过滤条件排序。

---

## 第四部分：Bloom Filter

### 4.1 Parquet 中的 Bloom Filter 实现

Parquet 2.0+ 可选支持 Bloom Filter，用于等值查询的高效过滤。Bloom Filter 是一种空间效率极高的概率性数据结构，能精确判断"元素一定不存在"，概率性判断"元素可能存在"。

**Thrift 定义：**

```thrift
struct BloomFilter {
  /** Bloom Filter 数据 */
  1: required binary bloom_filter
  /** 算法参数 */
  2: required BloomFilterHeader header
}

struct BloomFilterHeader {
  1: required i32 num_bytes           // 位数组大小
  2: required i32 num_hash_functions  // 哈希函数个数
  3: required binary algorithm        // 哈希算法
  4: required binary hash             // 最终哈希
}
```

**ColumnChunk 级关联（通过 meta_data 扩展）：**

```thrift
struct ColumnMetaData {
  // ... 其他字段
  /** Bloom Filter 在文件中的位置 */
  15: optional OffsetIndex bloom_filter_offset
  /** Bloom Filter 数据长度 */
  16: optional i32 bloom_filter_length
}
```

### 4.2 原理示意图

```
Bloom Filter 数据结构
┌───────────────────────────────────────┐
│  Bit Array (N bits)                   │
│  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐ │
│  │0│1│0│1│0│1│0│0│1│0│1│0│0│1│0│0│ │  ← 初始全 0
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘ │
│                                      │
│  插入 "user_123" →                   │
│    hash1("user_123") % N = 2  → bit 2=1 │
│    hash2("user_123") % N = 7  → bit 7=1 │
│    hash3("user_123") % N = 12 → bit 12=1│
│                                      │
│  查询 "user_999" →                   │
│    hash1("user_999") % N = 2  → bit 2=1 │
│    hash2("user_999") % N = 5  → bit 5=0 │→ ❌ 一定不存在
│    hash3("user_999") % N = 15 → bit 15=0│
│                                      │
│  查询 "user_456" →                   │
│    hash1("user_456") % N = 2  → bit 2=1 │
│    hash2("user_456") % N = 7  → bit 7=1 │
│    hash3("user_456") % N = 12 → bit 12=1│→ ✅ 可能存在（假阳性）
└───────────────────────────────────────┘
```

### 4.3 适用场景

| 场景 | Bloom Filter | ColumnIndex (min/max) |
|------|-------------|---------------------|
| `WHERE id = 123` | ✅ 精确过滤 | ❌ 范围大时无效 |
| `WHERE id IN (1,2,3)` | ✅ 逐值过滤 | ❌ 无效 |
| `WHERE id > 100` | ❌ 不支持范围 | ✅ 适用 |
| `WHERE name = 'Alice'` | ✅ 精确匹配 | ⚠️ 效果差（无序字符串） |
| `WHERE id IS NULL` | ❌ 不跟踪 NULL | ✅ 通过 null_count 过滤 |

### 4.4 写入和读取流程

```
写入流程（Writer）：

  写入每一行时
    → 对需要 Bloom Filter 的列
    → 将列值通过 K 个哈希函数映射到位数组
    → 设置对应位为 1
  ColumnChunk 写完
    → 序列化 Bloom Filter 位数组
    → 写入文件（ColumnChunk 数据之后）
    → 在 ColumnMetaData 中记录偏移和长度

读取流程（Reader）：

  解析 Footer
    → 获取 ColumnChunk.meta_data
    → 检查 bloom_filter_offset 是否存在
  执行 WHERE id = 123
    → 定位 Bloom Filter 位置（需随机读）
    → 加载 Bloom Filter 数据
    → 对 123 执行 K 次哈希
    → 检查所有位是否为 1
    → 任一为 0 → 该 Row Group 一定不含此值 → 跳过整个 Row Group
    → 全为 1 → 可能存在，需读取实际数据确认
```

### 4.5 Bloom Filter 参数选择

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `num_bytes` | 位数组大小（字节） | 根据列基数选择，基数 100k 约 1MB |
| `num_hash_functions` | 哈希函数个数 | 通常 3~5 |
| `false_positive_rate` | 假阳性概率 | 默认 1%（可配置） |
| `algorithm` | 哈希算法 | XXHASH64、MURMUR3 |

**假阳性率与位数组大小的关系（约算）：**

```
位数组大小 ≈ - (n * ln(p)) / (ln(2)^2)

n = 元素数量
p = 目标假阳性率

示例: n=1000000, p=0.01 → 位数组大小 ≈ 9.6 Mbit ≈ 1.2 MB
      哈希函数数 ≈ (m/n) * ln(2) ≈ 7
```

---

## 第五部分：与查询引擎的集成

### 5.1 Apache Spark

**支持级别：** 原生支持，自动启用

```
// Spark SQL 中谓词下推自动生效
spark.sql("SELECT * FROM parquet.`/data/table` WHERE id > 1000 AND name = 'Alice'")

// 物理计划可见 Filter 下推到 Parquet 扫描阶段
// == Physical Plan ==
// *(1) ColumnarToRow
// +- FileScan parquet [id, name, age]
//    DataFilters: [isnotnull(id), isnotnull(name), (id > 1000), (name = Alice)]
//    PushedFilters: [IsNotNull(id), IsNotNull(name), GreaterThan(id,1000), EqualTo(name,Alice)]
//    ReadSchema: ...
```

**Spark 中的谓词下推链路：**

```
Spark SQL 解析器
  → Catalyst Optimizer
    → FilterPushDown 规则
      → 提取可下推的 Filter（对 Parquet 支持的表达式）
      → 构造 PushedFilters
  → Parquet FileFormat 读取器
    → Row Group 裁剪（基于 statistics）
    → Page Index 裁剪（Spark 3.0+）
    → Bloom Filter 过滤（Spark 3.2+）
  → 读取命中的 Page 数据
    → 剩余 Filter（不支持下推的部分）在内存中过滤
```

**Spark 版本支持演进：**

| 版本 | 特性 |
|------|------|
| Spark 1.4 | 基本 Row Group 裁剪 |
| Spark 2.0 | 支持更多 Filter 类型下推（IN, IS NULL 等） |
| Spark 3.0 | 支持 Page Index（ColumnIndex/OffsetIndex） |
| Spark 3.2 | 支持 Bloom Filter 过滤 |
| Spark 3.4 | 增强嵌套列谓词下推 |

**限制：**
- 复杂表达式（LIKE、正则）不支持下推
- UDF 无法下推
- 嵌套类型（struct/map/array）的下推能力有限

### 5.2 DuckDB

**支持级别：** 深度集成，自动利用 Row Group 和 Page 级别统计

```
-- DuckDB 自动进行 Parquet 谓词下推
SELECT * FROM 'file.parquet' WHERE id > 1000;

-- 或者使用 parquet_scan 函数
SELECT * FROM parquet_scan('file.parquet', filter_pushdown=true);

-- 查看查询计划
EXPLAIN SELECT * FROM 'file.parquet' WHERE id > 1000;
-- ┌─────────────────────────────────────┐
-- │         PARQUET_SCAN                │
-- │   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
-- │   Filters: id>1000                  │
-- │   Filters (pushed down): id>1000    │
-- │   Files: file.parquet              │
-- │   Row Groups:                      │
-- │   └─ RowGroup 0: id=[1,5000] SKIP │  ← 直接显示裁剪
-- │   ...                               │
-- └─────────────────────────────────────┘

-- 检查页级别统计
SELECT * FROM parquet_metadata('file.parquet');
SELECT * FROM parquet_schema('file.parquet');
```

**DuckDB 的 Parquet 读取架构：**

```
DuckDB Parquet Reader
├── FileOpen → 读 Footer（4KB 小读）
├── RowGroupSelector
│   ├── 解析 statistics（内存操作）
│   └── 标记 Skip/Partial/Full
├── PageSelector (DuckDB 0.6+)
│   ├── 读 ColumnIndex（懒加载）
│   └── 标记哪些 Page 需要读取
├── BloomFilterSelector (DuckDB 0.8+)
│   ├── 等值查询时选择性加载 BF
│   └── 快速判断值不存在
└── ColumnReader
    └── 仅读取被标记的 Page
```

**DuckDB 优势：**
- 极致的延迟优化，Parquet 扫描性能在 OLAP 类引擎中领先
- 统计信息裁剪在 EXPLAIN 输出中透明可见
- 支持多文件全局统计裁剪

### 5.3 Apache Arrow Dataset

**支持级别：** 通过 `pyarrow.dataset` 显式支持

```python
import pyarrow.dataset as ds
import pyarrow.parquet as pq

# 方法 1: 使用 Dataset API（推荐）
dataset = ds.dataset("/data/table/", format="parquet")
table = dataset.to_table(
    filter=(
        (ds.field("id") > 1000) &
        (ds.field("name") == "Alice")
    ),
    columns=["id", "name", "age"]
)

# 方法 2: 使用 ParquetFile 的 Row Group 过滤
pf = pq.ParquetFile("/data/table/file.parquet")
metadata = pf.metadata

# 手动检查 Row Group 统计信息
for i in range(metadata.num_row_groups):
    rg = metadata.row_group(i)
    col = rg.column(0)  # id 列
    stats = col.statistics
    print(f"RG {i}: min={stats.min}, max={stats.max}")

# 方法 3: ParquetDataset（旧 API，已弃用倾向 dataset）
pq.ParquetDataset(
    "/data/table/",
    filters=[("id", ">", 1000), ("name", "=", "Alice")]
)
```

**Arrow Dataset 过滤下推流程：**

```
pyarrow.dataset.Dataset.to_table(filter=...)
  → 构造 Expression Tree
    → 分解为 Conjunctive Normal Form（合取范式）
    → 每个谓词单独评估可下推性
  → Fragment 扫描阶段
    → Row Group 裁剪（Arrow 14.0+ 自动）
    → Page Index 裁剪（Arrow 12.0+）
    → Bloom Filter 过滤（Arrow 14.0+）
  → 合并满足条件的 Row Group + Page
  → 只读取需要的数据

Expression 支持：
  ds.field("x") > 100              ✅
  ds.field("x").isin([1, 2, 3])    ✅
  ds.field("x").is_null()          ✅
  ds.field("x") == "Alice"         ✅
  ds.field("x") != "Bob"           ✅
  ds.field("x").between(10, 20)    ✅
  ~ds.field("x").is_null()         ✅
  (A) & (B) | (C)                  ✅ 复杂组合
```

### 5.4 parquet-cli / parquet-tools 元数据查看

```bash
# parquet-tools (Java, Apache Parquet 官方)
# 查看文件元数据（包含统计信息）
parquet-tools meta file.parquet

# 示例输出
# file schema: schema
# id:      INT64 OPTIONAL
# name:   BINARY OPTIONAL
# age:    INT32 OPTIONAL
#
# row group 0:  RC: 1000000  TS: 8.5 MB
# ---
# id:      INT64 SNAPPY DO:0 FPO:4  SZ: 1.2 MB/2.0 MB/1.0
#          ST: [min: 1, max: 5000, num_nulls: 0]
# name:    BINARY SNAPPY DO:0 FPO:6 SZ: 3.5 MB/5.2 MB/1.0
#          ST: [min: "Alice", max: "Bob", num_nulls: 10]
# age:     INT32 SNAPPY DO:0 FPO:8 SZ: 2.1 MB/3.1 MB/1.0
#          ST: [min: 18, max: 65, num_nulls: 2]

# 查看列索引（Parquet 2.0+）
parquet-tools column-index file.parquet

# 查看 Row Group 统计信息
parquet-tools row-group-size file.parquet

# parquet-cli (Apache Parquet 的 CLI 工具)
# 查看文件元数据
parquet-cli meta file.parquet

# 查看 Page 级别元数据
parquet-cli pages file.parquet

# Python 方式查看
python -c "
import pyarrow.parquet as pq
pf = pq.ParquetFile('file.parquet')
print(pf.metadata)
print(pf.metadata.row_group(0).column(0).statistics)
"
```

### 5.5 各引擎支持程度对比表

| 特性 | Apache Spark | DuckDB | Arrow Dataset | parquet-cli |
|------|:----------:|:-----:|:------------:|:----------:|
| **Row Group 裁剪** | ✅ 自动 | ✅ 自动 | ✅ 自动 | N/A（只读元数据） |
| **Page Index 裁剪** | ✅ 3.0+ | ✅ 0.6+ | ✅ 12.0+ | ✅ 可查看 |
| **Bloom Filter 过滤** | ✅ 3.2+ | ✅ 0.8+ | ✅ 14.0+ | ❌ 不支持 |
| **复合谓词下推** | ✅ AND/OR/IN | ✅ AND/OR/IN | ✅ AND/OR/IN | N/A |
| **LIKE 下推** | ❌ | ❌ | ❌ | N/A |
| **UDF 下推** | ❌ | ❌ | ❌ | N/A |
| **嵌套列下推** | ⚠️ 有限 | ⚠️ 有限 | ⚠️ 有限 | N/A |
| **多文件全局裁剪** | ✅ 分区裁剪 | ✅ | ✅ | N/A |
| **谓词下推透明化** | ✅ EXPLAIN | ✅ EXPLAIN | ❌ 隐式 | N/A |
| **统计信息查看** | ✅ 需编码 | ✅ parquet_metadata | ✅ 需编码 | ✅ 原生 |
| **自定义统计** | ❌ | ❌ | ❌ | N/A |

### 5.6 谓词下推效果参考基准

| 场景 | 列排序方式 | Row Group 裁剪率 | Page Index 裁剪率 | 总 I/O 减少 |
|------|-----------|:-------------:|:---------------:|:----------:|
| 范围查询 > WHERE | 按过滤列排序 | 30~50% | 20~40% | 50~80% |
| 范围查询 > WHERE | 未排序 | 0~10% | 0~10% | 0~20% |
| 点查询 = WHERE | 随机分布 | 0% | 0% | 0%（需 Bloom Filter） |
| 点查询 = WHERE + Bloom Filter | 任意 | 80~99% | N/A | 80~99% |
| BETWEEN (有序) | 按过滤列排序 | 30~60% | 30~50% | 60~85% |
| 多列 AND (有序) | 按首过滤列排序 | 30~60% | 20~40% | 50~80% |

**说明：** 实际效果高度依赖数据分布和查询模式。建议在写入 Parquet 时按高频过滤列排序（sorting/clustering），并启用 Bloom Filter 覆盖等值查询场景。

---

## 参考资料

1. Apache Parquet 格式规范: https://parquet.apache.org/docs/file-format/
2. Parquet Thrift 定义: https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift
3. Parquet ColumnIndex 提案: https://issues.apache.org/jira/browse/PARQUET-1201
4. Spark Parquet Filter Pushdown: https://spark.apache.org/docs/latest/sql-data-sources-parquet.html
5. DuckDB Parquet 扫描: https://duckdb.org/docs/data/parquet/overview
6. Arrow Dataset Filtering: https://arrow.apache.org/docs/python/dataset.html
7. Parquet Bloom Filter: https://github.com/apache/parquet-format/blob/master/BloomFilter.md
8. 基准数据参考: https://benchmark.clickhouse.com/
