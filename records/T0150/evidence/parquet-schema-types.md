# Parquet Schema & 类型系统专题

> T0154 — T0150 子任务：Parquet 格式深度技术调研
> 本文聚焦 Parquet 的物理类型、逻辑类型、嵌套模型、Schema Evolution 及 Oracle 类型映射。

---

## 1. Parquet 物理类型 (Physical Types)

Parquet 的物理类型定义列数据在磁盘上的原始二进制编码格式。共 7 种。

### 1.1 类型总览

| 物理类型 | 字节数 | 说明 | 状态 |
|----------|--------|------|------|
| `INT32` | 4 | 32 位有符号整数（小端补码） | 稳定 |
| `INT64` | 8 | 64 位有符号整数（小端补码） | 稳定 |
| `INT96` | 12 | 96 位有符号整数（小端补码），用于 Impala Hive 时间戳 | **已弃用** |
| `FLOAT` | 4 | IEEE 754 单精度浮点数（小端） | 稳定 |
| `DOUBLE` | 8 | IEEE 754 双精度浮点数（小端） | 稳定 |
| `BYTE_ARRAY` | 变长 | 长度前缀的字节序列（4 字节长度 + N 字节数据） | 稳定 |
| `FIXED_LEN_BYTE_ARRAY` | 固定 | 定长字节序列（在 schema 中声明长度） | 稳定 |

### 1.2 二进制表示

```
INT32 (值: 42)
  内存: 2A 00 00 00    (小端序)

INT64 (值: 42)
  内存: 2A 00 00 00 00 00 00 00

INT96 (值: 42 — 已弃用)
  内存: 2A 00 00 00 00 00 00 00 00 00 00 00  (12 字节)

FLOAT (值: 3.14)
  内存: C3 F5 48 40    (IEEE 754 单精度小端)

DOUBLE (值: 3.141592653589793)
  内存: 18 2D 44 54 FB 21 09 40    (IEEE 754 双精度小端)

BYTE_ARRAY (值: "Hello")
 ┌──────────┬──────────────────────┐
 │ 05 00 00 00 │ 48 65 6C 6C 6F      │
 │ 长度=5      │ 'H' 'e' 'l' 'l' 'o' │
 └──────────┴──────────────────────┘

FIXED_LEN_BYTE_ARRAY (值: UUID "550e8400-e29b-41d4-a716-446655440000")
 ┌──────────────────────────────────────────────────┐
 │ 55 0E 84 00 E2 9B 41 D4 A7 16 44 66 55 44 00 00 │
 │ 16 字节 (schema 声明 length=16)                    │
 └──────────────────────────────────────────────────┘
```

#### BYTE_ARRAY 存储细节

BYTE_ARRAY 在 Page 层面以两种方式编码：**Plain 编码** 使用 4 字节长度前缀（小端）后跟原始字节；**Dictionary 编码** 将字典索引存为 INT32，字典本身包含唯一值列表。

#### INT96 弃用说明

INT96 是 Hive/Impala 的历史产物，将纳秒时间戳存入 12 字节（前 8 字节为 Julian 日期的纳秒计数，后 4 字节为 Julian 日期）。Parquet 规范不再推荐使用，应使用 `INT64` + `TIMESTAMP` 逻辑类型替代。

---

## 2. 逻辑类型 (LogicalType / ConvertedType)

逻辑类型定义物理类型之上的语义层。Parquet 提供两套机制：

- **ConvertedType**（旧，v1.0 起）：enum 字段，有限表达能力
- **LogicalType**（新，v2.0+）：嵌套消息结构，更精确、可扩展

### 2.1 完整类型映射表

| 逻辑类型 | 物理载体 | ConvertedType | LogicalType 表示 | 编码说明 |
|----------|---------|---------------|-----------------|----------|
| `STRING` | `BYTE_ARRAY` | `UTF8` | `LogicalType::STRING` | UTF-8 编码字节序列 |
| `ENUM` | `BYTE_ARRAY` | `ENUM` | — | 枚举值的 UTF-8 名称 |
| `DECIMAL(p,s)` | `INT32/INT64/BYTE_ARRAY/FIXED_LEN_BYTE_ARRAY` | `DECIMAL` | `LogicalType::DECIMAL` | 有符号整数 ÷ 10^scale |
| `DATE` | `INT32` | `DATE` | `LogicalType::DATE` | Unix epoch 天数（有符号） |
| `TIME_MILLIS` | `INT32` | `TIME_MILLIS` | `LogicalType::TIME(isAdjustedToUTC, MILLIS)` | 午夜后毫秒数 |
| `TIME_MICROS` | `INT64` | `TIME_MICROS` | `LogicalType::TIME(isAdjustedToUTC, MICROS)` | 午夜后微秒数 |
| `TIMESTAMP_MILLIS` | `INT64` | `TIMESTAMP_MILLIS` | `LogicalType::TIMESTAMP(isAdjustedToUTC, MILLIS)` | Unix epoch 毫秒数 |
| `TIMESTAMP_MICROS` | `INT64` | `TIMESTAMP_MICROS` | `LogicalType::TIMESTAMP(isAdjustedToUTC, MICROS)` | Unix epoch 微秒数 |
| `TIMESTAMP_NANOS` | `INT64` | — | `LogicalType::TIMESTAMP(isAdjustedToUTC, NANOS)` | Unix epoch 纳秒数 (v2.0+) |
| `UINT_8` | `INT32` | `UINT_8` | `LogicalType::INTEGER(bitWidth=8, isSigned=false)` | 无符号 8 位 |
| `UINT_16` | `INT32` | `UINT_16` | `LogicalType::INTEGER(bitWidth=16, isSigned=false)` | 无符号 16 位 |
| `UINT_32` | `INT32` | `UINT_32` | `LogicalType::INTEGER(bitWidth=32, isSigned=false)` | 无符号 32 位 |
| `UINT_64` | `INT64` | `UINT_64` | `LogicalType::INTEGER(bitWidth=64, isSigned=false)` | 无符号 64 位 |
| `INT_8` | `INT32` | `INT_8` | `LogicalType::INTEGER(bitWidth=8, isSigned=true)` | 有符号 8 位 |
| `INT_16` | `INT32` | `INT_16` | `LogicalType::INTEGER(bitWidth=16, isSigned=true)` | 有符号 16 位 |
| `INT_32` | `INT32` | `INT_32` | `LogicalType::INTEGER(bitWidth=32, isSigned=true)` | 有符号 32 位 |
| `INT_64` | `INT64` | `INT_64` | `LogicalType::INTEGER(bitWidth=64, isSigned=true)` | 有符号 64 位 |
| `FLOAT16` | `FIXED_LEN_BYTE_ARRAY(2)` | — | `LogicalType::FLOAT16` | IEEE 754 半精度 (v2.0+) |
| `UUID` | `FIXED_LEN_BYTE_ARRAY(16)` | — | `LogicalType::UUID` | RFC 4122 大端字节序 |
| `JSON` | `BYTE_ARRAY` | `JSON` | `LogicalType::JSON` | JSON 文本的 UTF-8 字节 |
| `BSON` | `BYTE_ARRAY` | `BSON` | `LogicalType::BSON` | BSON 二进制数据 |
| `INTERVAL` | `FIXED_LEN_BYTE_ARRAY(12)` | `INTERVAL` | — | 月(4)+日(4)+毫秒(4) |
| `LIST` | 嵌套 Group | `LIST` | `LogicalType::LIST` | 集合类型 |
| `MAP` | 嵌套 Group | `MAP` | `LogicalType::MAP` | K-V 映射类型 |

### 2.2 DECIMAL 编码细节

```
DECIMAL(10, 2) 值: 12345.67
  存储值 = 12345.67 × 10^2 = 1234567

  物理类型选择规则:
  ┌────────────┬──────────────────────────────┐
  │ 精度范围     │ 推荐物理类型                  │
  ├────────────┼──────────────────────────────┤
  │ 1 ≤ p ≤ 9  │ INT32                        │
  │ 10 ≤ p ≤ 18│ INT64                        │
  │ 19 ≤ p ≤ 38│ BYTE_ARRAY (变长)            │
  │ 任意精度    │ FIXED_LEN_BYTE_ARRAY(ceil(p/2)) │
  └────────────┴──────────────────────────────┘

  编码: 有符号整数的二进制补码表示，除以 10^scale 得原始值。
```

### 2.3 TIMESTAMP_NANOS 编码

```
TIMESTAMP_NANOS 值: 2024-01-15 10:30:00.123456789 UTC
  Unix epoch 纳秒数 = 1705300200123456789
  INT64 存储: 17 AA 3D 7F 45 67 89 0F (小端)
  或: 使用 INT96 (已弃用)
```

### 2.4 逻辑类型在 Thrift 中的定义

LogicalType 使用 Thrift 联合体定义（`parquet.thrift`）：

```thrift
union LogicalType {
  1:  STRING      STRING;
  2:  MAP         MAP;
  3:  LIST        LIST;
  4:  ENUM        ENUM;
  5:  DECIMAL     DECIMAL;
  6:  DATE        DATE;
  7:  TIME        TIME;
  8:  TIMESTAMP   TIMESTAMP;
  9:  INTEGER     INTEGER;
  10: UNKNOWN     UNKNOWN;
  11: JSON        JSON;
  12: BSON        BSON;
  13: UUID        UUID;
  15: FLOAT16     FLOAT16;
}
```

---

## 3. 嵌套结构 Repetition 模型

### 3.1 三种 Repetition 类型

| Repetition | 语义 | 示例 |
|------------|------|------|
| `REQUIRED` | 必须出现恰好一次 | 非空标量字段 |
| `OPTIONAL` | 出现 0 或 1 次（可为 null） | 可空字段 |
| `REPEATED` | 出现 0 到 N 次（数组） | 列表元素 |

### 3.2 Dremel 嵌套模型

Parquet 的嵌套表达能力来源于 Google Dremel 论文（Melnik et al. 2010），通过 **Repetition Level (r)** 和 **Definition Level (d)** 两个标量值编码任意深度的嵌套结构。

- **Repetition Level (r)**：当前值和前一个值相比，在哪一层发生重复
- **Definition Level (d)**：当前值实际对应的路径深度（用于处理 null）

#### 核心算法

```
写入（Striping）:
  遍历嵌套结构的叶子值，记录每个值的 (r, d, value) 三元组

读取（Assembly）:
  按列扫描 (r, d, value)，根据 r 重建嵌套树
```

### 3.3 示例：JSON 嵌套结构的列式表示

```
示例 JSON:
{
  "a": [
    {"b": 1, "c": "x"},
    {"b": 2}
  ]
}

Schema 表示:
message root {
  optional group a (LIST) {
    repeated group bag {
      required group element {
        optional int64 b;       // d=0..3
        optional binary c (STRING);  // d=0..3
      }
    }
  }
}

列式 Striping 后的值序列:

列 a.bag.element.b:
  r=0, d=3, v=1   ← 新记录开始，路径完整
  r=2, d=3, v=2   ← 在 a.bag.element 层重复（数组第二个元素），路径完整
  └─ 每个值定义级别: 3 = 路径 a→bag→element→b 完全存在

列 a.bag.element.c:
  r=0, d=3, v="x"  ← 新记录开始，路径完整
  r=2, d=2, v=null ← 在 a.bag.element 层重复，但 element→c 不存在 (d=2 < 3)
  └─ 注意: c 在数组第二个元素中缺失，d=2 表示路径 a→bag→element 存在但 c 不存在
```

### 3.4 Definition Level 规则

```
对于路径 P = f1 / f2 / ... / fn，各字段的定义级别:
  - 若全部 REQUIRED: d 始终 = n（无需存储）
  - 若有 OPTIONAL 字段: d = 第一个为 null 的字段的深度

定义级别的最大值（max definition level）:
  = 路径中 OPTIONAL + REPEATED 字段的个数
  （REQUIRED 字段不贡献定义级别）

最小定义级别（标示值为 null）:
  = max definition level - 1
  （若该字段本身为 OPTIONAL；若为 REQUIRED 则无 null）
```

### 3.5 LIST 和 MAP 的标准表示

Parquet 规范对 LIST 和 MAP 有严格的嵌套要求（v2.0+）：

```
LIST 标准表示（v2）:
message root {
  required group my_list (LIST) {
    repeated group bag {
      optional element_type element;
    }
  }
}

MAP 标准表示:
message root {
  required group my_map (MAP) {
    repeated group bag {
      required key_type key;
      optional value_type value;
    }
  }
}
```

---

## 4. Schema Evolution

Parquet 支持有限的 Schema 演进化，遵循 **追加兼容** 原则。

### 4.1 规则的直观总结

```
旧 Schema           新 Schema            兼容性
────────────────────────────────────────────────
列 A, B             列 A, B, C           ✅ 兼容（新增列，reader 填 null）
列 A (INT32)        列 A (INT64)         ⚠️ 有限（宽度扩展可读）
列 A (BINARY)       列 A (INT32)         ❌ 不兼容
列 A                 列 B                 ❌ 不兼容（rename）
列 A, B, C           列 A, B             ⚠️ reader 自行忽略额外列
列 A REQUIRED        列 A OPTIONAL       ⚠️ 有限风险
```

### 4.2 新增列

- **允许**：reader 为缺失列填充 null（OPTIONAL）或抛出错误（REQUIRED）
- 新增 REQUIRED 列会破坏旧 reader：旧文件没有该列，无法满足 REQUIRED 约束
- 建议：始终将新列声明为 OPTIONAL

### 4.3 列类型变更兼容性矩阵

| 旧类型 | 新类型 | 兼容性 | 说明 |
|--------|--------|--------|------|
| INT32 | INT64 | ✅ 可安全读 | 零扩展（Zero-extend） |
| INT32 | FLOAT | ⚠️ 精度风险 | 大整数可能损失精度 |
| INT64 | DOUBLE | ⚠️ 精度风险 | 53-bit mantissa 可能截断 |
| FLOAT | DOUBLE | ✅ 安全 | 零扩展 |
| INT32 | DECIMAL | ⚠️ 需验证 | 若 DECIMAL 精度 ≤9 可兼容 |
| INT64 | DECIMAL | ⚠️ 需验证 | 若 DECIMAL 精度 10-18 可兼容 |
| INT8/16 | INT32/64 | ✅ 安全 | 宽度扩展兼容 |
| UINT8/16 | UINT32/64 | ✅ 安全 | 宽度扩展兼容 |
| STRING | BYTE_ARRAY | ✅ 兼容 | BYTE_ARRAY 是物理类型 |
| BINARY | STRING | ⚠️ 需验证 | 确认数据为合法 UTF-8 |
| STRING | INT | ❌ 不兼容 | 完全不同的二进制表示 |
| TIMESTAMP | INT64 | ⚠️ reader 依赖 | 需 reader 自行解释语义 |
| DATE | INT32 | ⚠️ reader 依赖 | 需 reader 自行解释语义 |
| INT96 | INT64+TIMESTAMP | ✅ 可转换 | 需工具转换，非直接兼容 |

### 4.4 列重命名

- **不兼容**：Parquet reader 按列名（SchemaElement.name）匹配
- 若重命名列，旧文件该列无法被新 reader 识别——reader 会忽略或报错
- 变通：保留旧列名，添加别名新列（数据冗余）

### 4.5 列删除

- **reader 侧兼容**：旧 reader 只需忽略不认识的列
- **writer 侧影响**：旧文件仍保留被删除列的数据
- 物理删除的代价：需重写整个 Parquet 文件

### 4.6 嵌套 Schema 变更规则

```
场景: 在 group 中添加/删除子字段
规则: 与顶层列相同——新增 OPTIONAL 子字段兼容，删除不破坏旧 reader

示例:
旧: message { optional group addr { optional int64 zip; } }
新: message { optional group addr { optional int64 zip;
                                      optional string city; } }
结果: ✅ 兼容——旧文件 addr.city 填 null

示例:
旧: message { optional group addr { optional int64 zip; } }
新: message { optional group addr { optional string zip; } }  -- 类型变更
结果: ❌ 不兼容——类型冲突
```

### 4.7 跨引擎互操作注意事项

| 引擎 | Schema 行为 | 注意点 |
|------|------------|--------|
| Spark | 读取时 schema merge 默认关闭 | `mergeSchema=true` 可自动兼容列增删 |
| Hive | 按 SerDe 读取，列名匹配 | `ALTER TABLE ... REPLACE COLUMNS` 要谨慎 |
| Presto/Trino | 按列名匹配，缺失列补 null | 对 schema 变更容忍度较高 |
| Arrow/PyArrow | `read_table` 支持列选择 | `schema` 参数可指定需要的列 |
| Impala | INT96 时间戳强依赖 | 迁移 INT96 列需显式转换 |

### 4.8 生产建议

```
Schema Evolution 黄金法则:
  1. 始终将新列声明为 OPTIONAL（而非 REQUIRED）
  2. 永远不重命名/删除列（除非重写文件）
  3. 仅做宽度扩展的类型变更（INT32→INT64, FLOAT→DOUBLE）
  4. 使用 LogicalType 标记语义（不要裸 INT32 当 DATE 用）
  5. 集中管理 schema registry 跟踪版本
```

---

## 5. Oracle → Parquet 类型映射建议

### 5.1 完整映射表

| Oracle 类型 | 推荐 Parquet 类型 | Physical Type | LogicalType | 说明 |
|-------------|-------------------|---------------|-------------|------|
| `VARCHAR2(n)` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 变长字符串 |
| `CHAR(n)` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 定长字符，需 trim |
| `NVARCHAR2(n)` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 统一用 UTF-8 |
| `NUMBER(p,0)` p≤9 | `INT32` | `INT32` | `INT_32` | 整数，无小数 |
| `NUMBER(p,0)` 10≤p≤18 | `INT64` | `INT64` | `INT_64` | 整数，无小数 |
| `NUMBER(p,0)` p≥19 | `DECIMAL(p,0)` | `BYTE_ARRAY` | `DECIMAL(p,0)` | 大整数 |
| `NUMBER(p,s)` s>0 | `DECIMAL(p,s)` | 按精度选 | `DECIMAL(p,s)` | 小数，保留精度 |
| `NUMBER` 无精度 | `STRING` 或 `DECIMAL(38,10)` | `BYTE_ARRAY` | 按需选 | 无约束 NUMBER 转字符串避免精度丢失 |
| `FLOAT` | `FLOAT` | `FLOAT` | — | IEEE 754 32-bit |
| `BINARY_FLOAT` | `FLOAT` | `FLOAT` | — | 等价映射 |
| `BINARY_DOUBLE` | `DOUBLE` | `DOUBLE` | — | IEEE 754 64-bit |
| `DATE` | `TIMESTAMP_MICROS` | `INT64` | `TIMESTAMP_MICROS` | Oracle DATE 含时分秒 |
| `TIMESTAMP` | `TIMESTAMP_MICROS` | `INT64` | `TIMESTAMP_MICROS` | 精确到微秒 |
| `TIMESTAMP(p)` p≤3 | `TIMESTAMP_MILLIS` | `INT64` | `TIMESTAMP_MILLIS` | 毫秒精度 |
| `TIMESTAMP(p)` 4≤p≤6 | `TIMESTAMP_MICROS` | `INT64` | `TIMESTAMP_MICROS` | 微秒精度 |
| `TIMESTAMP(p)` p≥7 | `TIMESTAMP_NANOS` | `INT64` | `TIMESTAMP_NANOS` | 纳秒精度（v2.0+） |
| `TIMESTAMP WITH TZ` | `TIMESTAMP_MICROS` + tz col | `INT64` | `TIMESTAMP(isAdjustedToUTC=true,...)` | 统一转 UTC |
| `CLOB` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 大文本 |
| `BLOB` | `BINARY` | `BYTE_ARRAY` | — | 二进制大对象 |
| `RAW(n)` | `FIXED_LEN_BYTE_ARRAY(n)` | `FIXED_LEN_BYTE_ARRAY` | — | 定长二进制 |
| `ROWID` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 物理行标识 |
| `UROWID` | `STRING` | `BYTE_ARRAY` | `STRING` / `UTF8` | 逻辑行标识 |
| `XMLTYPE` | `STRING` | `BYTE_ARRAY` | `JSON` 或 `STRING`/`UTF8` | XML 文本 |

### 5.2 NUMBER 类型映射决策树

```
NUMBER(p,s)
  ├─ s = 0  (整数)
  │   ├─ p ≤ 9       → INT32   (INT_32)
  │   ├─ 10 ≤ p ≤ 18 → INT64   (INT_64)
  │   └─ p ≥ 19      → DECIMAL(p,0) → BYTE_ARRAY
  ├─ s > 0  (小数)
  │   ├─ p ≤ 9       → DECIMAL(p,s) → INT32
  │   ├─ 10 ≤ p ≤ 18 → DECIMAL(p,s) → INT64
  │   └─ p ≥ 19      → DECIMAL(p,s) → BYTE_ARRAY / FIXED_LEN_BYTE_ARRAY(ceil(p/2))
  └─ 无精度约束 (NUMBER 裸申明)
      └─ 推荐: STRING → BYTE_ARRAY/UTF8
          备选: Spark 默认映射为 DECIMAL(38,10)
          注意: 裸 NUMBER 可存 ±9.99...×10^125，无通用物理类型完全覆盖
```

### 5.3 时间类型对比

| 精度 | Oracle 类型 | Parquet 载体 | 字节 | 范围 |
|------|-------------|-------------|------|------|
| 秒级 | `DATE` | INT64 → TIMESTAMP_MICROS | 8 | 纪元 ±292 年 |
| 毫秒 | `TIMESTAMP(3)` | INT64 → TIMESTAMP_MILLIS | 8 | 纪元 ±292 年 |
| 微秒 | `TIMESTAMP(6)` | INT64 → TIMESTAMP_MICROS | 8 | 纪元 ±292 年 |
| 纳秒 | `TIMESTAMP(9)` | INT64 → TIMESTAMP_NANOS | 8 | 纪元 ±292 年 |
| 旧版 Hive | 无直接对应 | INT96 (已弃用) | 12 | Julian 日期范围宽 |

**Oracle DATE vs Parquet DATE：**
- Oracle `DATE` 包含 **年/月/日/时/分/秒**
- Parquet `DATE`（逻辑类型）的物理载体为 INT32，存储 **Unix epoch 天数**
- Oracle DATE 应映射到 `TIMESTAMP_MICROS`（INT64），而非 Parquet 的 DATE 逻辑类型

### 5.4 CLOB / BLOB 映射细节

```
CLOB (Character Large Object):
  → 读取为 String → 写入 BYTE_ARRAY + StringType/UTF8
  → 大 CLOB (>2GB) 需分段读取
  → 注意字符集转换: Oracle AL32UTF8 → Parquet UTF-8

BLOB (Binary Large Object):
  → 读取为 byte[] → 写入 BYTE_ARRAY (无 LogicalType)
  → 大 BLOB 建议:
      方案 A: 直接存储为 BYTE_ARRAY（文件大小增长）
      方案 B: 外部存储 + 路径引用（Parquet 存外部路径）
  → BLOB 压缩建议: 写入 Parquet 时启用 snappy/zstd 压缩
     BLOB 通常已压缩（图片/文件），二次压缩收益有限，
     但若为未压缩二进制数据，zstd 可带来显著压缩比
```

### 5.5 精度与 null 处理

```
精度丢失风险点:
  NUMBER(38,0) → INT64  ❌ 可能溢出（INT64 最大 9.22e18 < 10^38）
  应使用 BYTE_ARRAY → DECIMAL(38,0)
  
  NUMBER → FLOAT/DOUBLE  ⚠️ 精度丢失
  NUMBER(10,2) = 99999999.99 → FLOAT ≈ 100000000.0
  若精度敏感，必须用 DECIMAL(p,s)

NULL 处理:
  Oracle NULL → Parquet OPTIONAL + Definition Level < max
  Oracle NOT NULL → Parquet REQUIRED（或 OPTIONAL + 非空约束）

空字符串:
  Oracle ''(空串) 被当作 NULL
  Parquet STRING 中空串 "" 与 NULL 不同
  映射时需处理: Oracle 空串 → Parquet NULL
```

### 5.6 Spark 默认映射参考

```
Oracle → Spark → Parquet 的默认映射（Spark JDBC）:

Oracle              Spark SQL           Parquet
────────────────────────────────────────────────
VARCHAR2/CHAR       StringType          BYTE_ARRAY + STRING/UTF8
NUMBER(p,s)         DecimalType(p,s)    INT32/INT64/BYTE_ARRAY + DECIMAL
NUMBER(无约束)      DecimalType(38,10)   BYTE_ARRAY + DECIMAL(38,10)
FLOAT/BINARY_FLOAT  FloatType           FLOAT
DOUBLE/BINARY_DOUBLE DoubleType         DOUBLE
DATE                DateType            INT32 + DATE
TIMESTAMP           TimestampType       INT64 + TIMESTAMP_MICROS
CLOB                StringType          BYTE_ARRAY + STRING/UTF8
BLOB                BinaryType          BYTE_ARRAY
RAW                 BinaryType          BYTE_ARRAY

注意: Spark 默认 NUM_PRECISION_RADIX = 38，
      超过 38 位的 DECIMAL 会被截断或报错，
      需在 fetch 时 CAST 为 STRING 后再写入。
```

---

## 附录 A：Parquet Thrift Schema 示例

```thrift
// 包含嵌套结构、LIST、MAP 和多种逻辑类型的完整 Schema
message oracle_export {
  required int64 id (INTEGER(64,true));           // Oracle NUMBER(18,0) → INT64
  required binary name (STRING);                   // Oracle VARCHAR2(100) → STRING
  optional binary email (STRING);                  // 可为空的 email
  optional int32 birth_date (DATE);                // Oracle DATE(仅日期部分) → DATE
  required int64 created_at (TIMESTAMP(MILLIS,true)); // Oracle TIMESTAMP → TIMESTAMP_MILLIS
  optional binary metadata (JSON);                 // Oracle CLOB(JSON) → JSON
  optional group addresses (LIST) {                // 嵌套数组
    repeated group bag {
      optional group element {
        required binary street (STRING);
        optional binary city (STRING);
        optional int64 zip (INTEGER(64,true));
      }
    }
  }
  optional group attributes (MAP) {                // K-V 映射
    repeated group bag {
      required binary key (STRING);
      optional binary value (STRING);
    }
  }
  optional fixed_len_byte_array(16) row_uuid (UUID); // Oracle RAW(16) → UUID
  optional double salary;                           // Oracle NUMBER(12,2) → via Decimal → Double
}
```

---

## 附录 B：参考资源

1. Parquet 格式规范: https://github.com/apache/parquet-format
2. Parquet Thrift 定义: https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift
3. Dremel 论文 (嵌套模型原始论文): https://dl.acm.org/doi/10.14778/1920841.1920871
4. Spark Parquet Schema Merge: https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#schema-merging
5. Oracle 数据类型文档: https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Data-Types.html
6. Parquet Logical Types: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md
