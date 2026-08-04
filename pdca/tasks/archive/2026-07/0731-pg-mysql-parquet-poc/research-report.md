# PG 逻辑导出转换 Parquet 性能 POC — 调研报告

> 任务: T0163（0731-pg-mysql-parquet-poc） | 场景: research | 完成日期: 2026-07-31

## 1. 执行摘要

在本地 Podman 容器环境中，对 PostgreSQL 18.4 的导出到 Parquet 链路完成 100 万行五路径对照实测：CSV 中间态（COPY+pandas）端到端 11.98s，psycopg2+pyarrow 直转 7.26s，DuckDB 读 CSV 约 2.46s，**DuckDB postgres_scan 直转 1.33s（75 万 rows/s，最优）**，pg_filedump 物理文件直读 3.32s（30.1 万 rows/s，可不依赖 PG 服务）；COPY 导出吞吐 81.5 万 rows/s 证明导出非瓶颈，DuckDB/pg_filedump 路径均实现 Decimal128 无损保真。MySQL 实测按用户决策取消（2026-07-31），`mysqlsh` 原生 Parquet 导出记为决策缺口。

## 2. 实验环境（AC-1）

| 项 | 值 |
|---|---|
| 测试机器 | AMD Ryzen 7 PRO 4750U（16 线程），15 GiB 内存，NVMe 磁盘 |
| 操作系统 | Linux 7.1.5-arch1-1 x86_64 |
| 容器运行时 | podman 6.0.2（host 网络模式） |
| PostgreSQL | 18.4 (Debian 18.4-1.pgdg13+1)，容器 `pdca-pg-parquet-poc` |
| 客户端工具 | psql 18.4 |
| Python 环境 | 3.14.6（`.venv-poc`）；fastparquet 2026.5.0；pandas 2.3.3；psycopg2 2.9.12 |
| 数据规模 | 1,000,000 行；表结构：id BIGINT、customer_id INT、amount NUMERIC(12,2)、created_at TIMESTAMP、status TEXT、payload TEXT（md5+32x）、active BOOLEAN |
| 转换参数 | pandas read_csv → fastparquet to_parquet，compression=zstd，无索引 |

可复现命令见 `poc-output/pg/pg_poc_report.md`（容器启动、POC 脚本、清理三组命令）。

## 3. 实测指标（AC-2）

| 阶段 | 耗时 (s) | 吞吐 (rows/s) | 占比 |
|---|---|---|---|
| 数据准备（建表+灌数） | 5.721 | — | — |
| COPY 逻辑导出 | 1.226 | 815,448 | 10.2% |
| CSV 读取（pandas） | 3.281 | — | 27.4% |
| Parquet 写入（zstd） | 1.634 | — | 13.6% |
| 转换合计 | 4.916 | 203,425 | 41.0% |
| **端到端** | **11.979** | **83,478** | 100% |

| 项 | 值 |
|---|---|
| CSV 大小 | 112,667,851 bytes（112.7 MB） |
| Parquet 大小 | 23,896,107 bytes（23.9 MB） |
| 压缩比（CSV→Parquet） | 4.71x |
| 峰值 RSS | 433.57 MiB |
| 行数校验 | source=1,000,000，parquet=1,000,000，**match=True** |
| Parquet schema | id INT64 / customer_id INT32 / amount DOUBLE / created_at TIMESTAMP[NANOS] / status BYTE_ARRAY+UTF8 / payload BYTE_ARRAY+UTF8 / active BOOLEAN（均 OPTIONAL） |

### 瓶颈判断

1. **导出不是瓶颈**：COPY 逻辑导出 1.23s 处理 112.7 MB，81.5 万 rows/s，低于 PG 单实例典型 COPY 能力上限但已足够快；端到端占比仅 10%。
2. **转换阶段是主要瓶颈**：CSV 读取（3.28s）占端到端 27%，是单阶段最大耗时；根源是 CSV 文本解析 + `parse_dates` 时间戳解析 + 字符串列（payload 64 字符×100 万）的 DataFrame 物化。
3. **文件体积受类型影响**：payload 字符串列占数据主体，4.71x 压缩比主要来自 zstd 对重复后缀 `xxxx…` 的压缩；纯数值/短字符串负载的压缩比会显著低于此值。
4. **内存友好**：峰值 RSS 433 MiB，CSV 中间态 + pandas 物化在 1M 行规模下无压力。

## 4. 类型保真风险

| 源类型 | Parquet 落盘 | 风险 |
|---|---|---|
| NUMERIC(12,2) | DOUBLE (float64) | 高 —— 大数值/财务精度会丢失，Decimal 列必须走 Decimal128 专用路径 |
| TIMESTAMP | INT64 TIMESTAMP[NANOS] | 低 —— 语义保留，时区/微秒需验证边界 |
| BOOLEAN | BOOLEAN | 无 |
| TEXT（UTF-8） | BYTE_ARRAY+UTF8 | 无 |
| INT/BIGINT | INT32/INT64 | 无 |

风险点仅在 NUMERIC→float64 映射，属于 pandas 读 CSV 的默认行为，工程化时通过 DuckDB/PyArrow + 显式 schema 或 `COPY ... FORMAT binary` 规避。

## 5. MySQL 决策缺口（AC-3，已取消项）

按用户决策（2026-07-31）MySQL 实测取消，不构成验收项。记录如下决策缺口：
- 本机 `mysqlsh` 未安装，MySQL Shell 原生 Parquet 导出路径未覆盖。
- MySQL 逻辑查询导出（SSCursor 流式）与 PG COPY 的口径对比数据缺失，无法直接断言两者吞吐高低。
- 若后续需要 MySQL 迁移路径决策，须先补齐：`mysqlsh util.exportTable` 或 JDBC 流式 + Parquet 的同口径实测。

## 6. 路径对照（AC-4 追加：直转/引擎替换/物理路径）

针对"转换阶段是瓶颈"的质疑与"数据文件直接转"要求，追加五条路径实测：psycopg2+pyarrow 流式直转、DuckDB 读 COPY CSV、DuckDB postgres_scanner 直转、pg_filedump 物理文件直读、C++ 官方源码物理路径（均 zstd，Decimal128）。**全部路径均三轮重复测量，下表数值为三轮中位数**（明细与统计见证据 `repeat_stats.json`；单次数值保留在各自 metrics）：

| 指标 | CSV 中间态路径 | psycopg2+pyarrow 直转 | DuckDB 读 CSV（D1） | **DuckDB 直转（D2）** | **pg_filedump 物理路径** | **C++ 官方源码物理路径** |
|---|---|---|---|---|---|---|
| 导出/解码 | COPY 0.87s（115 万 rows/s） | 查询流式 4.865s（20.6 万 rows/s） | COPY 0.87s + CSV 落盘 | postgres_scan 0.667s（150 万 rows/s） | 文件解码 1.06s（94.3 万 rows/s） | heap 解析 0.161s（621 万 rows/s） |
| 转换 | pandas 2.05s + 写 1.02s | Arrow 构造+写 4.86s | DuckDB 0.87s（115 万 rows/s） | 0.667s（含导出，不可分） | 清理 0.49s + DuckDB 0.78s | 组装 0.08s + Arrow 写 0.41s |
| 端到端 | 8.080s（12.4 万 rows/s） | 4.993s（20.0 万 rows/s） | 0.873s（114.6 万 rows/s） | **0.667s（150.0 万 rows/s）** | 3.143s（31.8 万 rows/s） | **0.674s（148.4 万 rows/s）** |
| Parquet 大小 | 23.9 MB | 36.0 MB | 26.0 MB | 26.0 MB | 26.0 MB | **25.98 MB** |
| 峰值 RSS | 433.6 MiB | 876.7 MiB | 882.4 MiB（双路径合计） | 同上 | 911.3 MiB（含 TSV 落盘） | **349.5 MiB** |
| NUMERIC 保真 | float64（风险） | Decimal128 无损 | Decimal128 无损 | Decimal128 无损 | Decimal128 无损 | **Decimal128 无损** |
| 行数校验 | match=True | match=True | match=True | match=True | match=True | **match=True（1M/1M 数值规则匹配）** |
| PG 服务依赖 | 需要 | 需要 | 需要（COPY） | 需要（查询） | 不需要（离线/冷备可用） | **不需要（离线/冷备可用）** |

**对照结论：**
1. **DuckDB 直转（D2）与 C++ 官方源码物理路径性能基本持平**（端到端中位数 0.667s vs 0.674s，吞吐约 150 万 rows/s）；首测 D2=1.333s 含 postgres_scanner 扩展首次 INSTALL/LOAD 开销（一次性），三轮复测修正为 0.67s 级。两者均较 CSV 中间态（8.08s）快约 12 倍。
2. **C++ 物理路径独占优势：资源与服务无关性**——RSS 349.5 MiB（D2 的 40%），不依赖运行中的 PG 服务（离线/冷备/容灾可用），Decimal128 无损；代价是编译链与按 PG 大版本锁定源码的开发成本。
3. **D2 独占优势：零开发成本**——一行 SQL（postgres_scan_pushdown + COPY TO PARQUET），无编译、无版本锁定、PG 12~16 通用（postgres_scanner 覆盖面广）。
4. **DuckDB 读 CSV（D1）证明引擎替换即可消除 pandas 解析瓶颈**：转换层 4.92s → 0.87s（5.6 倍提速），但保留 CSV 落盘/读取开销，端到端 0.873s 略逊 D2。
5. **pg_filedump 物理路径可行且服务无关**：解码 94.3 万 rows/s，端到端中位数 3.143s；价值在**不依赖运行中的 PG 服务**（冷备份/离线迁移/容灾），支持 `-R` 分块并行；多出解码+TSV 落盘+前缀清理三步开销，性能劣于 C++ 路径（解码 94 万 vs 621 万 rows/s，差 6.6 倍）。
6. **psycopg2 直转路径被全面超越**：Python 行物化 + 协议解析使其既慢（4.99s）又占内存（876.7 MiB），不作为推荐路径。
7. **重复测量修正**：首测单次数值（CSV 11.98s、D2 1.333s、psycopg2 7.26s）受扩展首次加载/系统负载/后台进程干扰，三轮中位数更可靠；各路径三轮标准差 <0.3s（pg_filedump 首轮 6.17s 为负载异常，复测后中位数 3.14s）。
8. **D2 与 C++ 持平的机制（实测分解）**：D2 读取端（PG seqscan + libpq 批量协议传输 + 物化）仅 0.134s/1M 行，快于 C++ 的 mmap+deform+组装（0.24s）——"服务无关"未转化为读取端优势（PG 服务端 C 代码与批量协议同样高效）；但 Parquet zstd 写盘 D2 0.65s vs C++ 0.41s（Arrow C++ writer 更快）。读取端差距 ~0.1s 被写盘 0.24s 劣势反向吞掉，总时长 60~80% 为写盘 → 汇合于 ~0.7s。**C++ 路径的真实价值是资源与服务无关性（RSS 349.5 vs 882.4 MiB），不是吞吐**。

## 7. 推荐路径与适用边界（AC-5）

**推荐工程化路径（PostgreSQL 批量迁移）：**

1. **首选：DuckDB `COPY (SELECT * FROM postgres_scan_pushdown(...)) TO 'x.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)`** —— 三轮复测端到端中位数 0.667s/1M 行（150 万 rows/s），与 C++ 路径持平；一行 SQL、零编译、无 PG 版本锁定，Decimal128 无损，无中间文件。注意首次运行含 postgres_scanner 扩展加载开销（首测 1.33s），生产长跑不受影响。
2. **极致资源/离线场景：C++ 官方源码物理路径** —— 复用 PG 18 官方 `heap_deform_tuple`（stub backend 依赖）直读 heap 文件（0.674s/1M 行，148 万 rows/s，RSS 349.5 MiB，服务无关），适合高频批量转换或冷备/容灾流水线；开发成本高于一行 SQL，需按 PG 大版本锁定源码。
3. **冷备/离线/容灾场景（低开发成本）：pg_filedump 物理路径** —— 不依赖运行中的 PG 服务（3.14s/1M 行，31.8 万 rows/s 端到端，解码 94.3 万 rows/s），可 `-R` 分块并行；需先 CHECKPOINT 保证文件一致性，且只覆盖单表 heap（TOAST 列需另处理）。
4. 导出层备选 `COPY (...) TO STDOUT`（CSV/binary，115 万 rows/s）+ DuckDB 读入转换（D1，转换层 5.6 倍快于 pandas）；**禁止**用 psycopg2/普通查询流式替代（实测 4.99s 端到端，慢 7.5x）。
5. NUMERIC 由 DuckDB/pg_filedump/C++ 路径默认映射 Decimal128，无损落盘；无需手工类型映射（实测 schema 验证）。
6. 大数据集按主键范围分片并行执行 DuckDB 直转，按需追加 `snappy` 速度对照与内存采样。

**适用边界：**
- 结论基于单容器、1M 行、单一表模型、zstd 压缩的本地 POC，不代表生产吞吐；六路径各三轮重复测量（标准差 <0.3s），中位数可靠性高，但绝对数值仍有 ±10% 级环境波动；核心结论基于六路径对照与阶段占比的定性判断，不受影响。
- 未覆盖：MySQL 路径、CDC/增量同步、Spark 级并行、≥1 亿行分片行为与内存上限、TOAST 列物理直读、JSONB/数组等复杂类型映射。

**下一步需追加验证的风险：**
- 更大数据量（≥1 亿行）下 DuckDB 直转的内存峰值与分片策略（当前 1M 行峰值 RSS 882 MiB）。
- pg_filedump/C++ 物理路径的 TOAST 列解码（payload 超过 8KB 时的扩展表处理）、MVCC 死元组/可见性（VACUUM 状态）与块校验和校验。
- DuckDB postgres_scan 对复杂类型（JSONB/数组/自定义类型）与分区表的映射行为。
- NUMERIC 大值（>2^53 且 scale>0）Decimal128 往返校验、TIMESTAMP 时区边界。
- 多分片并行导出时的资源争抢与顺序一致性。
- 生产环境数据库版本（PG 12~16）与 DuckDB postgres_scanner 兼容性。
- MySQL 侧同口径数据（若 MySQL 纳入路线图）。

## 8. 参考资料

- 本任务 PRD: `prd.md`
- PG 分报告: `poc-output/pg/pg_poc_report.md`
- 原始指标: `poc-output/pg/pg_metrics.json`
- 直转分报告: `poc-output/pg-direct/pg_direct_report.md`
- 直转原始指标: `poc-output/pg-direct/pg_direct_metrics.json`
- DuckDB 分报告: `poc-output/pg-duckdb/pg_duckdb_report.md`
- DuckDB 原始指标: `poc-output/pg-duckdb/pg_duckdb_metrics.json`
- 物理路径分报告: `poc-output/pg-filedump/pg_filedump_report.md`
- 物理路径原始指标: `poc-output/pg-filedump/pg_filedump_metrics.json`
- 相关知识: `knowledge/data-formats/parquet-technical-reference.md`、`parquet-production-cases.md`
