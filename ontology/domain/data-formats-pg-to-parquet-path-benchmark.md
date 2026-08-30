---
schema: pdca.asset/v1
id: ontology:domain/data-formats-pg-to-parquet-path-benchmark
type: domain
layer: Knowledge
status: active
summary: PostgreSQL → Parquet 转换路径性能对照（实测）
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
  testable_signal: 由领域实践与测试验证
---

# PostgreSQL → Parquet 转换路径性能对照（实测）

> 来源：T0163（0731-pg-mysql-parquet-poc）Check 结论，PG 18.4 本地实测（zstd、Decimal128、单表 7 列模型）。

## 六路径与实测（1M 行，三轮中位数）

| 路径 | 端到端 | 吞吐 | 峰值 RSS | PG 服务依赖 | 判定 |
|---|---|---|---|---|---|
| CSV 中间态（COPY→pandas） | 8.08s | 12.4 万 rows/s | 433.6 MiB | 需要 | 劣：最慢、float64 精度风险 |
| psycopg2+pyarrow 流式直转 | 4.99s | 20.0 万 rows/s | 876.7 MiB | 需要 | 劣：慢 7.5 倍+内存高，禁用 |
| DuckDB 读 COPY CSV（D1） | 0.87s | 114.6 万 rows/s | 882.4 MiB | 需要 | 中：消除 pandas 瓶颈，留中间态开销 |
| **DuckDB postgres_scanner 直转（D2）** | **0.67s** | 150.0 万 rows/s | 882.4 MiB | 需要 | 优(1M 并列)：零开发成本 |
| pg_filedump 物理文件直读 | 3.14s | 31.8 万 rows/s | 911.3 MiB | **无需** | 中：离线可用，解码+TSV+清理开销 |
| **C++ 官方源码物理路径** | **0.67s** | 148.4 万 rows/s | **349.5 MiB** | **无需** | 优(1M 并列)：内存最低、离线可用 |

## 规模敏感性（100M 行，实测 D2 与 C++）

| 路径 | 端到端 | 吞吐 | 峰值 RSS |
|---|---|---|---|
| D2 | 86.31s | 115.9 万 rows/s | **2084.6 MiB** |
| **C++ 物理** | **74.69s** | 133.9 万 rows/s | **403.4 MiB** |

**关键规律：1M 持平 → 100M C++ 反超 13.5%**。机制：D2 写盘随行数劣化（100M ≈73s vs C++ ≈56s），读取端 D2 优势（PG seqscan，线性外推 ≈13s vs C++ parse 17.8s）不足以抵消；D2 内存 2GB 级（缓冲物化压力），C++ 批处理内存与行数解耦（恒定 ~400 MiB）。

## 推荐矩阵

- ≤1M 行：D2（零成本）或 C++（资源/离线），并列首选；pg_filedump 仅离线/冷备工具链。
- ≥100M 行：**C++ 物理路径全面占优**（速度+13.5%、内存−80%、服务无关）；D2 需分片并行与内存规划（10 亿+ 行风险显著）。
- CSV/psycopg2 任何规模不推荐；D1 仅在"已有 COPY 产物"存量流程中有替换价值。

## 工程化注意

- D2 首跑含 postgres_scanner INSTALL/LOAD 一次性开销（首测 1.33s），长跑不受影响。
- 普通查询流式导出（psycopg2）慢 7.5 倍，禁止作为工程化导出方式。
- 正确性口径：count、distinct id、数值规则（amount=(id%100000)/100）、status 分布四重校验，Decimal128 无损。
- 物理路径前置：CHECKPOINT 保证文件一致性；heap 分段（>1GB 拆 .1/.2...）需拼接为连续文件（各段整页，cat 合并后按全局偏移/BLCKSZ 索引）；TOAST 列需另处理。
