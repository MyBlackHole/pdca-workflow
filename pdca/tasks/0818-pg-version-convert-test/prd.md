# T0301 PostgreSQL 各版本数据文件转换测试（PRD）

## 问题

T0250 已实现 PG 物理直读（heap + CLOG → Parquet，pgbin 编译依据 PG18.4），但仅实测单版本
PG18.4。PG 的物理解析存在版本差异：heap 头字段偏移（t_infomask：PG12+ @20，PG11- @24，
因 PG12 移除 t_xvac 4B 前移）与 CLOG 目录名（PG10+ `pg_xact/`，PG9.x 及更早 `pg_clog/`）。
pg_clog_legacy_pg9.c 目前占位恒 -1，未实现。需要验证 pgbin 在各版本的转换正确性。

## 目标

对 PostgreSQL **9.6 / 11 / 18** 三版本（覆盖全部差异节点：pg_clog 目录 / 偏移 24 / 偏移 20）
各执行一次完整 heap+CLOG 物理直读→Parquet 转换测试，实现 PG9.x pg_clog 读取与 pgbin
运行时版本适配，逐版本全量对照 SQL 基准（1M 行×7 列）。

## 用户故事

作为数据转换工具使用者，我希望 pgbin 能正确读取不同 PG 版本的数据文件，
以便在多版本 PG 环境（9.x/10-11/12+）下离线转换为 Parquet，且结果与 SQL 完全一致。

## 实现/测试决策（已确认方向）

1. **版本集**：{9.6, 11, 18}——覆盖 pg_clog（9.x）/ t_infomask 偏移 24（10-11）/ 偏移 20（12+）
2. **PG9.x CLOG**：实现 `pg_clog_legacy_pg9.c`（`pg_clog/` 目录，SLRU 32 页/段、2-bit xid 状态
   与 pg_xact 一致，仅目录名不同；复用 pg10.c 已验证的 SLRU 逻辑，分派按目录）
3. **pgbin 运行时适配**：新增 `--pg-version=<9.6|11|18>`（默认 18 兼容现行为）；
   按版本运行时选择 heap 头偏移（PG12+：infomask@20/t_hoff@22/natts@18/头24B；
   PG11-：infomask@24/t_hoff@26/natts@22/头28B）；
   字段解码由 PG18 heaptuple.c 的 `heap_deform_tuple` 改为**按版本偏移自解码**
   （poc_orders 7 列类型已知：int8/int4/numeric/timestamp/text/text/bool，
   按 t_hoff 数据起点 + natts + null bitmap + 类型手动解码；text varlena TOAST 外置跳过）
4. **测试深度**：全量逐字段对照（差异=0 为通过，含聚合）
5. **数据源**：各版本容器独立灌数 1M（`bench/gen_pg_versions.py`，generate_series 倍增）

## 验收标准

- [ ] AC-1: 三版本容器（postgres:9.6/11/18）就绪，各版本 poct25.poc_orders 独立灌数，
      SQL count = 1,000,000
- [ ] AC-2: 各版本干净关闭固化（heap + CLOG：9.6/11=`pg_clog/`，18=`pg_xact/`），
      提取至 evidence/pg/versions/{96,11,18}/
- [ ] AC-3: pg_clog_legacy_pg9.c 实现（pg_clog/ 目录 SLRU 读取），PG9.6 直读 count 与 SQL 一致
- [ ] AC-4: pgbin `--pg-version` 运行时适配（heap 头偏移按版本分派 + 字段自解码），
      三版本转换 rows 均 = 1,000,000
- [ ] AC-5: 三版本 parquet 与 SQL 全量逐字段对照差异数 = 0（1M×7 列，含聚合）
- [ ] AC-6: 每版本转换测试记录（md）写入 evidence/pg/versions/，manifest.jsonl 登记；
      PG18 基线（默认 --pg-version=18 无参数）无回归

### 声明的测试接缝
- seam: bench/verify_version_convert.py -> src/pg/pg_heap_reader.c
- seam: bench/verify_version_convert.py -> src/pg/pg_clog_reader_pg10.c
- seam: bench/verify_version_convert.py -> src/pg/pg_clog_legacy_pg9.c
- seam: bench/verify_version_convert.py -> src/pg/pgbin.cpp
- seam: bench/gen_pg_versions.py -> 三版本容器（建表灌数）
- seam: bench/extract_version_pg.sh -> 容器 volume（heap+CLOG 固化提取）

## 范围外

- PG TOAST 外置/压缩值读取（text 外置跳过，与 T0250 一致）
- PG 中间版本（10/12/14/16）、PG9.0-9.5
- WAL 崩溃恢复一致性、在线增量

## 备注

- 测试数据（heap/CLOG/parquet/SQL 基准）不入 pdca 仓库，仅记录引用
- 参考：T0300（MySQL 四版本转换测试，全量对照模板/页序陷阱）、T0250（PG 直读原型+AC-10）
- pgbin 参数将统一为 `<heap> <clog_dir> <out> [--rows=] [--pg-version=]`（对齐 mysqlbin 风格）