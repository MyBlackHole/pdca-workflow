---
schema: pdca.asset/v1
id: T0163-0731-pg-mysql-parquet-poc
phase: check
source_ids: [research-report, pg-poc-report, pg-metrics, pg-direct-report, pg-direct-metrics, pg-duckdb-report, pg-duckdb-metrics, pg-filedump-report, pg-filedump-metrics, pg-cpp-report, pg-cpp-metrics, repeat-stats, cpp-100m]
---

# T0163 — PG 逻辑导出转换 Parquet 性能 POC — 结论

## 上下文

为支撑 PostgreSQL 批量迁移工程化路径决策，在本地 Podman 容器中对 PG 18.4 执行 100 万行导出 → Parquet 的六路径对照实测：CSV 中间态（COPY→pandas）、psycopg2+pyarrow 流式直转、DuckDB 读 COPY CSV、DuckDB postgres_scanner 直转、pg_filedump 物理文件直读、C++ 官方源码物理路径（复用 PG 官方 `heap_deform_tuple` + Arrow C++ 写 Parquet）。MySQL 实测按用户决策取消（2026-07-31），仅登记 `mysqlsh` 缺口。按用户追加要求，另在 1 亿行表（poc_orders_big，只建一次）上实测最高优先两路径（C++ 物理 vs DuckDB 直转）。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 导出到 Parquet 链路在本地可复现实测 | 达成：六路径各三轮重复测量（中位数），行数校验均 match=True |
| 瓶颈定位（导出 vs 转换） | 转换阶段占 CSV 路径端到端 38%，是主要瓶颈；COPY 导出仅占 10.8%（0.87s） |
| 转换瓶颈可被直转路径消除 | 达成：DuckDB 直转端到端中位数 0.667s（150 万 rows/s），比 CSV 路径快 12.1 倍、比 psycopg2 直转快 7.5 倍 |
| PG 数据文件可直接转 Parquet | 达成：pg_filedump 物理路径端到端中位数 3.143s（31.8 万 rows/s，解码 94.3 万 rows/s）；C++ 官方源码物理路径 0.674s（148.4 万 rows/s，RSS 349.5 MiB），均不依赖运行中的 PG 服务 |
| NUMERIC 精度风险可消除 | 达成：DuckDB/pg_filedump/C++ 默认 Decimal128(12,2) 无损落盘（amount 规则 1M/1M 精确匹配） |
| 数据体积与压缩 | CSV 路径 23.9 MB（float64）；DuckDB/pg_filedump 26.0 MB、C++ 25.98 MB（Decimal128），无显著体积代价 |
| 资源消耗 | CSV 路径峰值 RSS 433.6 MiB；DuckDB 双路径 882.4 MiB；pg_filedump 911.3 MiB（含 TSV 落盘）；C++ 349.5 MiB（六路径最低），1M 行规模无压力 |
| 1 亿行规模：C++ 物理 vs D2 直转 | 达成（含规模敏感性验证）：C++ 74.69s（133.9 万 rows/s，RSS 403.4 MiB）反超 D2 86.31s（115.9 万 rows/s，RSS 2084.6 MiB）13.5%；1M 时两路径持平（0.674 vs 0.667s）。机制：D2 写盘随行数线性劣化（1 亿行 ≈73s vs C++ ≈56s），读取端优势（PG seqscan ≈13s vs C++ 17.8s）不足以抵消；D2 内存 1 亿行达 2GB 级 |

## 分析

- 导出层（COPY）吞吐 115 万 rows/s 充足；**普通查询流式导出（psycopg2）实测慢 7.5 倍，禁止作为工程化导出方式**。
- **DuckDB 直转（D2）与 C++ 官方源码物理路径性能持平**（0.667s vs 0.674s，约 150 万 rows/s）；首测 D2=1.333s 含 postgres_scanner 首次加载开销，三轮复测修正。D2 优势在零开发成本（一行 SQL、无版本锁定）；C++ 路径优势在资源（RSS 349.5 MiB，D2 的 40%）与服务无关性（离线/冷备/容灾可用），代价是编译链与按 PG 大版本锁定源码。
- pg_filedump 物理路径的价值在服务无关性（冷备份/离线迁移/容灾），解码速度快（94.3 万 rows/s）但端到端多出解码+TSV 落盘+前缀清理开销（3.143s）；需 CHECKPOINT 保证一致，TOAST 列另处理。
- DuckDB 读 CSV（D1）证实"pandas CSV 解析是转换瓶颈"的替代解释，引擎替换即 5.6 倍提速（0.873s）；但保留 CSV 落盘/读取开销，端到端略逊 D2。
- **1 亿行规模反转（追加验证）**：C++ 物理路径 74.7s 反超 D2 86.3s（快 13.5%），与 1M 行持平格局不同；分阶段计时显示 D2 写盘劣化是主因（写盘 ≈73s vs C++ ≈56s，读取端 D2 ≈13s 仍快于 C++ 17.8s）。D2 内存峰值 1 亿行 2084.6 MiB（C++ 403.4 MiB 的 5.2 倍），10 亿+ 行需分片策略；C++ 批处理内存与行数解耦。两条路径 1 亿行全量校验通过（count/distinct/amount 规则/status 分布），无规模退化；C++ 批处理改造中修复三个 bug（结构体布局不一致、批量边界游标漏行、上限误用 batch）。
- 六路径各三轮重复测量（标准差 <0.3s），中位数可靠性高；测量窗口存在后台进程干扰（遗留 opencode、挂起 apt-get、tmpfs 空间），已复测并如实记录，绝对数值仍有 ±10% 级环境波动；核心结论基于六路径对照与阶段占比的定性判断，不受影响。
- MySQL 取消是范围决策而非环境失败，缺口已显式登记。

## 适用边界

- 仅覆盖 PostgreSQL 单库、单表模型、zstd、单容器本地环境；不代表生产吞吐。
- 已实测至 1 亿行（C++ 物理与 D2 直转两路径）；未覆盖：MySQL 路径、CDC/增量同步、Spark 级并行、10 亿+ 行与 D2 分片策略、TOAST 列物理直读、JSONB/数组复杂类型映射、PG 12~16 兼容性。

## 下一轮建议

1. DuckDB 直转 10 亿+ 行的分片策略与内存上限验证（1 亿行 RSS 已达 2GB 级）。
2. pg_filedump/C++ 物理路径的 TOAST 列解码、MVCC 可见性（VACUUM 状态）与块校验和验证。
3. DuckDB postgres_scan 复杂类型（JSONB/数组/自定义类型）与分区表映射验证。
4. NUMERIC 大值（>2^53 且 scale>0）Decimal128 往返校验、TIMESTAMP 时区边界。
5. 生产 PG 版本（12~16）与 DuckDB postgres_scanner 兼容性验证。
6. 若 MySQL 纳入路线图，按同表模型补齐同口径实测。
