---
schema: pdca.asset/v1
id: ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-research-report
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats-t0250-mysql-parquet-physical-evidence-research-report/1.0.0
summary: 调研报告 — MySQL / PostgreSQL 数据文件直接转换 Parquet
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
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 调研报告 — MySQL / PostgreSQL 数据文件直接转换 Parquet

> T0250（0813-mysql-parquet-physical）| 场景：research | 阶段：do 收口
> 仓库：`/home/black/Documents/database_转换_parquet` | 日期：2026-08-14

## 1. 问题与目标

数据仓库 / 数据湖迁移需要把 MySQL、PostgreSQL 存量数据导出为列式 Parquet。常规路径为逻辑导出
（mysqldump / mysqlsh / pg_dump / binlog→CDC）或 DuckDB scanner 直连，均依赖在线 DB 或副本。
本调研探索**离线物理文件直读**：不启动数据库、不依赖 binlog，直接从数据文件（InnoDB .ibd / PG heap）
按物理格式解析并转 Parquet，评估其可行性、正确性、性能与工程化方案。

**目标**：产出双库同口径的可行路径实测结论与可运行 C/C++ 原型，正确性以"物理直读行数与 SQL count
及值一致"为硬性验收。

## 2. 方案与实测结果

### 2.1 MySQL InnoDB 物理直读（AC-1/3/4/7/8）

工具：`build/mysqlbin`（C + Arrow C++ 写 Parquet，SDI 驱动通用解析）。

- **页遍历**：FIL_PAGE_TYPE=24 判 INDEX，B+tree 叶页（PAGE_LEVEL=0）沿记录链 next 偏移遍历；
  COMPACT/DYNAMIC 行格式，`rec_init_offsets_comp_ordinary` 语义解 offsets（NULL 位图 LSB 起 / 变长
  len 反序 / DATA_BIG_COL 2B + 0x4000 external 位）。
- **类型解码**：INT/BIGINT/DECIMAL(12,2)/DATETIME(6)/TIME2/ENUM/SET/VARCHAR/TEXT/BLOB 全类型，
  整数与 DECIMAL 首字节 ^0x80 符号位翻转；DATETIME2 5B 位域 + fsp 分数缩放；TIME2 负值反码补码。
- **版本探测**：5.6/5.7（无 SDI，走 `--schema=` CLI 参数化）/ 8.0 / 8.4 各 1M 行均可解析，
  行数与 SQL count 一致（差异=0，AC-1）。**版本差异要点**：5.6 默认 COMPACT（其余 DYNAMIC），
  8.0+ SDI 页内嵌表定义（5.6/5.7 在 .frm，需 schema 参数化）；页/记录编码四版本一致；
  off-page LOB 仅验证 8.0.13+ 新版（type 24/23），旧 BLOB 页（type 22）未覆盖。
- **可见性**：关闭后无活跃事务，聚簇索引记录非 delete-mark 即可见；`REC_INFO_DELETED_FLAG` 过滤，
  UPDATE/DELETE/ROLLBACK/ReadView 冻结 5 场景物理直读行数 == SQL count（差异=0，AC-4）。
- **off-page**：新版 LOB（8.0.13+）TEXT 大值经 20B REF 定位 LOB_FIRST 页 data@696；
  9000B（外部）/7000B（本地不溢出）已逐字节核对一致；多档长度补验（AC-8）：64KB（65536B）经
  FIRST+4×DATA 段拼接，以及 3000~100000 共 16 档（含 8192 本地/外置阈值、15680 单段上限、
  2/3/5/7 多段）全部逐字节一致，见 EVIDENCE.md。
- **页压缩**：KEY_BLOCK_SIZE=8 COMPRESSED 表压缩页（FIL_PAGE_COMPRESSED=14）zlib 解压后按普通页
  解析，控制信息 @26 起（V1：version/alg/orig_type/orig_size/comp_size）（AC-7）。
- **TDE**：`--keyring` 参数，keyring_file 主密钥（XOR 混淆串）→ 页0 `lCC` key_info（AES-256-ECB）
  → 表空间密钥/IV，页两阶段 AES-256-CBC 解密（C++ 实现，见 tde_decrypt.*）。
  加密样本 200000 行与 Python GOLD 全量逐值一致（AC-7）。

### 2.2 PG 物理直读（AC-2/3/4）

工具：`build/pgbin`（heap + pg_xact→Parquet）。

- heap 页遍历 + 行头 xmin/xmax；**CLOG（pg_xact）精确判断提交状态**（非启发式）。
  **PG12+ heap 头 t_infomask 偏移 20（非旧文档 24）**；FROZEN hint-bit（INVALID|COMMITTED
  同置）需先判 FROZEN 再判 INVALID（AC-10 修复）。
- 1M 行与 PG count 一致；四事务场景（INSERT/UPDATE/DELETE/ROLLBACK）visible == SQL count
  差异=0。关键前提：**heap 与 pg_xact 必须同快照**（只拷 heap 不重拷 CLOG 会误判全 invisible）。
- 边界：TOAST 压缩 varlena 识别跳过计数、NULL/空串/emoji/numeric 极值/历史时间戳正确。

### 2.3 性能对照（AC-5，1M 行，≥3 轮中位数）

| 路径 | 中位耗时 s | 吞吐 rows/s | 峰值 RSS | Parquet 大小 |
|---|---|---|---|---|
| MySQL 物理直读（mysqlbin） | 1.789 | 558,985 | 1138 MB | 22.7 MB |
| PG 物理直读（pgbin） | 1.061 | 942,288 | 307 MB | 24.8 MB |
| DuckDB mysql_scanner | 4.640 | 215,528 | 54 MB | 45.7 MB |
| DuckDB postgres_scanner | 1.301 | 768,405 | 54 MB | 49.4 MB |

物理直读采用列类型映射（decimal128/timestamp(us)/boolean），Parquet 更紧凑（约为 DuckDB 通用
VARCHAR 物化的 1/2）；MySQL 物理直读吞吐 ≈ DuckDB mysql_scanner 的 2.6 倍，PG 略高于 scanner。

### 2.4 100M 首选路径（AC-6，8.0）

数据：`poc_orders_100m` 100,000,000 行（id 11~1,011,000,000，payload VARCHAR(96) 小值），
干净关闭固化 `.ibd` 5.88 GB（359,374 页 / 16 KiB）。

| 路径 | rows | 耗时 s | 吞吐 rows/s | Parquet 大小 |
|---|---|---|---|---|
| mysqlbin 物理直读（全量单次） | 100,000,000 | 68.3 | 1,463,755 | 634 MB |
| DuckDB mysql_scanner（3 轮流中位数） | 100,000,000 | 285.97 | 349,693 | 494 MB |

- 两路 rows=100,000,000 均与 SQL `COUNT(*)` 一致；**物理直读快 4.2×**（285.97/68.3）。
- Parquet 大小差 28%：物理直读类型化（INT64/FLBA/BOOLEAN）vs scanner 通用 VARCHAR 物化 + 字典压缩。
- 工程注意：固化 .ibd 必须干净关闭后拷贝；大文件勿放 tmpfs（拷贝被 quota 截断会致行数减半，
  以 `SHOW TABLE STATUS Data_length` 与文件大小核对可快速暴露）。

### 2.5 PG 100M 直读回归（AC-10，详见 evidence/pg/ac10_pg_100m_frozen_fix.md）

数据：`poc_orders_100m` 100,000,000 行，干净关闭固化 heap（7,249,559,552 B = 884,956 页 × 8 KiB）
+ pg_xact/0000（CLOG 与 heap 同快照）。

| 指标 | 修复前 | 修复后 |
|---|---|---|
| rows | 65,581,895 | **100,000,000** |
| skipped_invisible | 34,418,105 | **0** |
| 吞吐 | — | 1.90M rows/s |
| SQL `COUNT(*)` 差异 | -34,418,105 | **0** |

- **根因**：`HEAP_XMIN_FROZEN = COMMITTED|INVALID` 两 bit 同置，`pg_tuple_visible`
  先判 `XMIN_INVALID→invisible`，把 34.4% frozen 行全误判（且 PG12+ heap 头
  t_infomask 偏移 20，非旧文档 24）。
- **修复**：INVALID 置位时先排除 FROZEN（COMMITTED 同置→可见），仅纯 INVALID 判 aborted。
- PG 100M 物理直读（1.90M rows/s）≈ DuckDB postgres_scanner（768K rows/s）的 2.5×。

### 2.6 工程坑位速记（AC-6 实测）

- 自引用 `INSERT INTO t ... SELECT ... FROM t`（binlog=ROW）易触发锁等待超时回滚：先 `CREATE TABLE src AS SELECT * FROM t`
  物化源表再插入可规避（188K 行/s）。
- DuckDB 1.5.x 已移除 `mysql_scan()`，改用 `LOAD mysql_scanner; ATTACH 'host=... user=... password=... database=...' AS x (TYPE mysql);`。

## 3. 风险矩阵

| 风险 | 等级 | 现状与缓解 |
|---|---|---|
| InnoDB 版本页格式差异（5.6~8.4） | 中 | 已四版本实测通过；SDI（8.0+）通用 / schema 参数化（5.6/5.7） |
| TDE 密钥链还原 | 中高 | 已 C++ 全链路实现并 GOLD 对拍一致；仅支持 keyring_file v2 单 AES 条目 |
| 页压缩 zlib 解压 | 中 | 已实现 KEY_BLOCK_SIZE=8 解压验证 |
| off-page LOB 多段 | 中→低 | 新版 LOB_FIRST/REF 已通；64KB（5 段）与 3000~100000 16 档已全部逐字节验证（AC-8） |
| CLOG 与 heap 快照一致性 | 高 | 必须同快照拷贝，已文档化并验证 |
| `innodb_fast_shutdown=2` 冷关闭 redo 重放 | 高 | 明确范围外；前置要求正常关闭固化 |
| 内存 | 低 | TDE 整文件明文缓冲=ibd 大小，真实大表需批处理化（已记录） |

## 4. 推荐工程化方案

1. **MySQL 侧**：mysqlbin（SDI 驱动）为核心，扩展压缩页/TDE/off-page 已具备；建议
   - 批处理化 TDE 解密（避免整文件明文内存）；
   - 压缩页解压与 TDE 解密整合进页读取统一层；
   - 后续可支持 undo/二级索引直读（当前范围外）。
2. **PG 侧**：pgbin（CLOG 可见性）为核心，快照一致性必须工具化（heap+pg_xact 原子拷贝）。
3. **双库统一**：同一 Arrow writer（src/common）、同一评测框架（bench/、DuckDB 对照），
   建议扩展为配置驱动（DB 类型 + 数据文件 + schema）。
4. **正确性保障**：所有路径保留 SQL count 全量对照 + 聚合校验作为 CI 门禁。

## 5. 适用边界

- **适用**：实例正常关闭后的 .ibd 快照、PG CHECKPOINT 后数据目录；离线/迁移/归档场景；
  表级直读（SDI 驱动）；1M~100M 行规模实测。
- **不适用**：崩溃恢复（`fast_shutdown=2` / redo 重放）后的数据一致性；在线增量同步；
  分布式并行 10 亿+；加密 undo / advanced redo 等企业特性；PG btree 有序枚举（T0165）。

## 6. 结论

双库**离线物理直读→Parquet 全链路可行且正确**：MySQL InnoDB 四版本、TDE、页压缩、off-page 与
PG CLOG 可见性均通过"直读 vs SQL 差异=0"硬验收；性能物理直读 ≥ DuckDB scanner（MySQL 侧约 2.6 倍）。
推荐以 mysqlbin/pgbin 为核心、配置驱动统一框架工程化，正确性 CI 门禁化。

## 7. 产出清单

- 原型：build/mysqlbin、build/pgbin；源码 src/mysql/、src/pg/、src/common/
- 证据：evidence/mysql/、evidence/pg/（EVIDENCE.md、ac1_four_versions.md、ac5_benchmark.md、.ibd 快照）
- 评测：bench/（数据生成 + 场景构造）
- 知识沉淀：ontology/domain/data-formats/mysql-innodb-physical-read-notes.md
