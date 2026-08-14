# PRD — T0250 调研 MySQL、PG 数据文件直接转换 Parquet

> 场景：research | 阶段：plan | 日期：2026-08-13

## 1. 问题陈述

- **现状**：T0163 已实证 PG 逻辑导出+物理路径（pg_filedump、C++ heap 直读），MySQL 侧实测被取消，物理路径空白；T0165 正在深化 PG 难点（MVCC/TOAST/btree）但采用启发式可见性（未读 CLOG）。PG/MySQL 数据文件直接转 Parquet 缺乏**双库同口径**的完整方案与工程化结论。
- **目标**：调研并实测 MySQL、PostgreSQL 数据文件（物理文件）直接转换成 Parquet 的可行路径、正确性（可见性）、性能与工程化方案，产出可运行原型与双库对照结论。
- **差距**：① MySQL InnoDB .ibd 物理直读方案无任何实测数据；② PG 可见性依赖启发式，未用 CLOG 精确判断；③ 双库无统一评测口径；④ 页压缩/TDE/off-page 溢出页解码无验证。

## 2. 目标与验收标准

### AC-1 MySQL InnoDB .ibd 物理直读原型（C/C++）

在 `/home/black/Documents/database_转换_parquet` 交付可运行 InnoDB 物理直读→Parquet 原型（C/C++ + Arrow C++ 写 Parquet）。支持：

- 表空间页遍历（FIL_PAGE_INDEX）、B+tree 叶链/记录解析、COMPACT/DYNAMIC 行格式
- 记录解码（INT/INT32/BIGINT/NUMERIC/DECIMAL/TIMESTAMP/TEXT/BLOB/BOOL）、NULL 位图
- schema 由 CLI 参数化传入（列名/类型/行格式），不读 .frm/数据字典
- 版本探测：5.6/5.7/8.0/8.4 各生成 .ibd 均可解析

**Pass 标准**：四个版本各建 7 列表灌 1M 行，原型全部解析成功且行数与 SQL count 一致（差异=0）。

### AC-2 PG 物理直读模块重写（含 CLOG 可见性）

在统一评测框架下重写 PG 物理直读模块（不直接复用 T0163 遗留 main.cpp），**纳入 CLOG（pg_xact）读取判断 xmin/xmax 提交状态**，非纯启发式。

**Pass 标准**：PG 18 实例建 7 列表灌 1M 行，解析行数与 SQL count 一致；四事务场景可见性实验（见 AC-4）通过。

### AC-3 数据模型与边界表

沿用 T0163 7 列模型：id BIGINT、customer_id INT、amount DECIMAL(12,2)、created_at TIMESTAMP、status TEXT、payload TEXT（md5+32x）、active BOOLEAN。另建边界表：NULL 列、空串、DECIMAL 极值（±9999999999.99）、BLOB 大值（>8KB 触发 off-page）、emoji/多字节特殊字符。

**Pass 标准**：边界表全行解析成功，值与 SQL SELECT 逐一匹配（每行相等）。

### AC-4 可见性硬性验收（双库 4 事务场景）

双库各构造 4 场景并做**物理直读 vs SQL count 全量对照**，差异=0：

| # | 场景 | 操作 |
|---|---|---|
| V1 | INSERT 基准 | 灌 1M 行后关闭 |
| V2 | UPDATE 造死元组/历史版本 | UPDATE 20 万行后关闭（不 VACUUM/purge） |
| V3 | DELETE 造 delete-mark | DELETE 5 万行后关闭 |
| V4 | 回滚事务残留 | 开事务 UPDATE 后 ROLLBACK 再关闭 |

**Pass 标准**：V1~V4 四场景，PG 与 MySQL 各场景物理直读行数 == SQL count（差异=0）。PG 走 CLOG 判断；MySQL 跳过 delete-marked 记录。

### AC-5 性能对照（1M，双库同口径，与 T0163 方法论一致）

| 路径 | 说明 |
|---|---|
| PG 物理直读（重写模块） | 统一框架 |
| MySQL InnoDB 物理直读 | 统一框架 |
| DuckDB postgres_scanner 直转 | 对照（T0163 D2 基线） |
| DuckDB mysql_scanner 直转 | 对照 |

各 ≥3 轮取中位数；指标：端到端耗时、吞吐 rows/s、峰值 RSS、Parquet 大小、Decimal128 保真、行数校验。

**Pass 标准**：四路径各 ≥3 轮实测，中位数表交付；PG 结果与 T0163 存档交叉核对（量级一致）。

### AC-6 100M 首选路径（8.0）

MySQL 8.0 上 1 亿行：InnoDB 物理直读 vs DuckDB mysql_scanner 全路径对照（端到端/吞吐/RSS/Parquet 大小/校验）。

**Pass 标准**：两路径 100M 全量校验通过（count=100,000,000）；对照数据入表。

### AC-7 页压缩 + TDE 验证

- 页压缩：建 `COMPRESSED` 表（KEY_BLOCK_SIZE=8），验证物理直读对压缩页的解压解码
- TDE：开启 `innodb_file_per_table` 表空间加密（file-based keyring），验证加密页读取（含密钥文件处理）

**Pass 标准**：压缩表与加密表各灌 ≥1000 行，直读行数==SQL count，抽样值匹配。

### AC-8 off-page 溢出页解码

TEXT/BLOB 大值（>页面内联上限，DYNAMIC/COMPRESSED 表）经 off-page 溢出页完整解码，非截断/置 NULL。

**Pass 标准**：payload 3KB/8KB/64KB 三档大值各 ≥100 行，直读值==SQL 值（逐字节）。

### AC-9 双库统一评测与知识沉淀

产出：双库同口径对照表（1M 全路径 + 100M 首选）、调研报告（可行性/路径/风险/推荐工程化方案）、knowledge 沉淀（MySQL InnoDB 物理直读要点 + 双库转换方案对照）。

**Pass 标准**：对照表含 AC-5/AC-6 全部路径数据；报告覆盖问题/方案/取舍/适用边界；knowledge 资产登记入 manifest。

## 验收标准

- [ ] AC-1 MySQL 四版本 .ibd 物理直读原型可运行，行数与 SQL count 一致（差异=0）
- [ ] AC-2 PG 物理直读模块含 CLOG 可见性，1M 行数与 SQL count 一致
- [ ] AC-3 7 列模型 + 边界表全行解析，值与 SQL 逐一匹配
- [ ] AC-4 V1~V4 四场景双库可见性对照差异=0
- [ ] AC-5 四路径 1M 各 ≥3 轮中位数对照表，PG 与 T0163 交叉核对
- [ ] AC-6 MySQL 8.0 100M 两路径对照，全量校验通过
- [ ] AC-7 压缩表与 TDE 加密表直读验证通过
- [ ] AC-8 off-page 三档大值解码逐字节匹配
- [ ] AC-9 双库统一对照表 + 调研报告 + knowledge 沉淀登记

## 3. 方案设计

### 3.1 代码仓库与结构

- 位置：`/home/black/Documents/database_转换_parquet`（当前目录建仓）
- 语言：C/C++，Arrow C++ 写 Parquet；评测脚本 Python（同 T0163 方法论）
- 模块：
  - `innodb_reader`：表空间页解析、B+tree 遍历、记录解码、压缩页解压、TDE 解密、off-page 读取
  - `pg_reader`：heap 解析 + CLOG 可见性判断
  - `pgbin`：统一 Arrow 组装 + Parquet 写出
  - `bench/`：评测脚本、四版本容器编排、场景实验脚本

### 3.2 MySQL 四版本环境

| 版本 | 用途 | 行为 |
|---|---|---|
| 5.6 | 可读性验证 | 建表灌数→shutdown→直读解析 |
| 5.7 | 1M 全量性能 | 完整对照 |
| 8.0 | 1M 全量 + 100M + 压缩/TDE/off-page | 完整对照 + 专项 |
| 8.4 | 可读性验证 | 建表灌数→shutdown→直读解析 |

统一 podman 容器（host 网络，仿 T0163 PG 容器模式）；关闭统一 `innodb_fast_shutdown=1`。

### 3.3 可见性方案

- **MySQL**：聚簇索引记录无 delete-mark 即可见（关闭后无活跃事务，旧版本在 undo 不在数据页）；跳过 delete-marked 与已提交删除残留
- **PG**：读 CLOG（pg_xact）判断 xmin/xmax 提交状态，构建精确可见性；V4 回滚场景与 V2 死元组场景验证 CLOG 路径
- 正确性兜底：AC-4 四场景 count 全量对照

### 3.4 一致性前置

- MySQL：实例正常关闭（`innodb_fast_shutdown=1`）→ .ibd 快照；`=2` 冷关闭（需 redo 重放）明确范围外
- PG：CHECKPOINT 后拷贝数据目录（等价 T0163 前置）

## 4. 范围外

- `innodb_fast_shutdown=2` 冷关闭/崩溃恢复后的 redo 重放一致性
- MySQL 逻辑导出路径（mysqlsh / mysqldump / binlog→CDC）实测
- PG 侧 btree 有序枚举（T0165 独立推进）；TOAST 物理直读实现
- 在线/增量同步；分布式并行；10 亿+ 行
- 压缩页/TDE 之外的企业特性（如 advanced redo、加密 undo）
- 二级索引物理直读（仅聚簇索引）

## 5. 风险

- **InnoDB 版本差异**：5.6~8.4 页格式/记录头/SDI 位置差异，四版本解析需版本分支适配；以实测页内容为准（同 T0165 对 btree 的处理）
- **TDE 密钥链**：file-based keyring 主密钥→表空间密钥层级，需还原 MySQL 加密算法（AES-256-XTS），实现复杂度中高
- **压缩页**：KEY_BLOCK_SIZE 页压缩（zlib）解压 + 记录偏移修正
- **CLOG 解析**：pg_xact 文件布局/SLRU 语义，需对照 PG 源码
- **环境**：四 MySQL 容器磁盘/内存（100M 表 8.0）；podman host 网络端口规划
- **工期**：InnoDB 解析器为最大工程项，AC-7/AC-8 为可降级项（若 TDE/压缩阻塞则以风险记录交付）

## 6. 产出

- 原型代码（`database_转换_parquet` 仓库）：innodb_reader / pg_reader / pgbin / bench
- research-report.md（可行性、路径、风险矩阵、推荐工程化方案、适用边界）
- evidence：双库对照表、metrics JSON、四版本复现手册、场景实验脚本
- knowledge 沉淀：MySQL InnoDB 物理直读要点 + PG/MySQL 双库数据文件转换对照