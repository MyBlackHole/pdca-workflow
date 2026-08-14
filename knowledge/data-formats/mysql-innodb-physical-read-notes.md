# MySQL InnoDB 物理直读 → Parquet 工程要点

> 来源：T0250（records/T0250-0813-mysql-parquet-physical）。离线直读 InnoDB `.ibd` / PG
> heap，不启动数据库服务，用 Arrow C++ 写 Parquet。完整源码副本见同目录 `src/`，
> 验收证据见 `evidence/`。直接复用可避免踩坑。

## 架构

- **mysqlbin**（src/mysql/）：.ibd → parquet。
  - 8.0+ 由 SDI 页（FIL_PAGE_SDI，type 17853）zlib JSON 表定义**自动推导物理布局**；
  - 5.6/5.7 无 SDI，走 `--schema=<file>` CLI 参数化（列名/类型/行格式，布局含
    PK + DB_TRX_ID 6B + DB_ROLL_PTR 7B + 其余列）；
  - 可选 `--keyring=`（TDE 解密）、`--rows=`（限行）。
- **pgbin**（src/pg/）：heap + pg_xact → parquet，CLOG 精确判断 xmin/xmax 提交状态。
- **统一 Arrow writer**（src/common/）：列类型映射写出 Parquet（ZSTD）。

## InnoDB 页/记录格式要点（对照 percona-xtrabackup 8.0 源码）

- 页常量：`FIL_PAGE_TYPE`@24（INDEX=17855 / SDI=17853 / LOB_FIRST=24 / LOB_DATA=23 /
  FIL_PAGE_COMPRESSED=14），`FIL_PAGE_DATA`=38、`PAGE_N_RECS`=54、`PAGE_LEVEL`=64。
- 记录头（extra 5B，在 origin 前）：byte0 = `info_bits<<4 | n_owned`（
  `REC_INFO_DELETED_FLAG=0x20` 位2 → delete-mark 跳过）；byte3-4 = next =
  **相对当前 origin 的有符号偏移**（`next_offs = rec + (int16)field`）。
- 变长字段长度数组位于 origin 前（nulls 区 0 字节则全 NOT NULL）。
- **整数**：InnoDB 大端 + **有符号首字节 ^0x80**（BIGINT 1 → `80 00..01`）。
- **DECIMAL(12,2)**：6B = [符号+intg 高位 1B][intg_lo 4B BE][frac 1B]，
  `intg=(b0&0x7F)*1e9+be32(b1..4)`。
- **DATETIME(6)**：8B = 5B 位域 + 3B 微秒；日期位域 `ym<<22|day<<17|hour<<12|min<<6|sec`，
  ym=year*13+month（**month 0-indexed**）。
- 聚簇索引物理列序 = [id][DB_TRX_ID 6B][DB_ROLL_PTR 7B][其余用户列]（系统列需占位对齐 offsets，输出跳过）。

## off-page LOB 多段（8.0 新版 LOB，AC-8 实测）

- **阈值**：<8192B 本地存记录；**≥8192B off-page**。
- 记录内 20B REF：`space 4B | page 4B | offset 2B | version 2B | len 8B` BE → LOB_FIRST 页。
- LOB_FIRST 页内 index list：flst base@64（len 4B + first fil_addr 6B）；index array 固定
  10 entry × 60B → **data_begin=696**。
- entry（index_entry_t）：PREV@0/NEXT@6（fil_addr 6B）/PAGE_NO@48 4B/**DATA_LEN@52 2B**。
- 首段（PAGE_NO==FIRST 自身）数据在页内 **@696**；其余段命中 LOB_DATA 页时 payload 在
  **@49**（本版本实测）。沿 NEXT 链拼接 → 多段完整值（65536B → 15680 + 4×16327…尾段）。
- 实测段结构：15680 内单段；16300+ → 2 段；32768 → 3 段；65535 → 5 段；100000 → 7 段。

## TDE / 页压缩

- **TDE**（--keyring）：keyring_file 主密钥（XOR 混淆串）→ 页0 `lCC` key_info
  （AES-256-ECB）→ 表空间密钥/IV；页两阶段 AES-256-CBC 解密（尾部 32B trailer 先解，
  拼前部 16314B 解主区；type 从原 type@28 恢复）。**关闭 EVP 默认 PKCS#7 padding**。
- **页压缩**（type 14）：控制信息 @26 起（version/alg zlib/orig_type/orig_size/comp_size），
  zlib 解压后与 38B 头拼接、恢复 orig_type 并清零控制字段。

## 可见性

- **MySQL**：正常关闭后无活跃事务，跳过 delete-mark 记录即可见。已删除记录 purge 后会
  从链上消失（PAGE_N_RECS 减少），两种状态遍历结果都正确。保留 delete-mark 需后台 RR
  事务建旧 ReadView 阻塞 purge 后再运行中拷 .ibd。
- **PG**：CLOG（pg_xact）精确判断；**FROZEN hint-bit = INVALID|COMMITTED 同置**，判定顺序
  必须先查 INVALID 时是否 COMMITTED（frozen → 可见），仅纯 INVALID 判 aborted。
  PG12+ heap 头 t_infomask 偏移 20（非旧文档 24）。heap 与 pg_xact **必须同快照**。

## 快照一致性（关键坑）

- MySQL：**禁止 `podman stop` 触发关闭**（不 flush InnoDB 脏页 → BLOB 页丢失）。
  正确流程：`SET GLOBAL innodb_fast_shutdown=0` + 容器内 `mysqladmin shutdown` 全量刷盘
  → 再拷 .ibd。`fast_shutdown=2`/redo 重放范围外。
- 大文件勿放 tmpfs（实测 5.3G ibd 被截断致行数减半，对比 SHOW TABLE STATUS 暴露）。

## 性能基线（本机，ZSTD）

- 1M 行：MySQL 1.789s/558K rows/s（RSS 1138MB，mmap+Arrow 缓冲）；PG 1.061s/942K rows/s；
  DuckDB mysql_scanner 4.640s / postgres_scanner 1.301s（通用 VARCHAR 物化，Parquet 约 2×大）。
- 100M 行（8.0）：mysqlbin 68.3s/1.46M rows/s（634MB parquet）vs DuckDB mysql_scanner
  285.97s/350K rows/s → **快 4.2×**；PG 100M 1.90M rows/s。
- 正确性校验以"直读 vs SQL count/值差异=0"硬验收（四版本 1M、四事务场景、压缩/TDE/off-page 全档）。

## 目录

- `src/` 关键源码（mysqlbin / pgbin / 统一 Arrow writer）
- `evidence/` 验收证据与调研报告（ac1 四版本 / ac5 1M 四路径 / ac7 100M 对照 / EVIDENCE /
  ac10 PG frozen 回归 / research-report / manifest）
- `bench/` 数据生成脚本与 schema（gen_mysql/gen_mysql_versions/gen_mysql_scenarios/
  gen_scenarios_pg + *.schema）
- `tools/` 页/记录验证工具（dump_ibd/hexpage/trav/parse_rec/probe/tde_decrypt.py 等）
- 注：测试数据（.ibd 快照 / parquet 输出 / 100M 基准 json）不入此仓库，保留于源项目
  `/home/black/Documents/database_转换_parquet/evidence/` 与 `data/100m/`（见 manifest.jsonl 资产清单）
