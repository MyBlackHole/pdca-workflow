# T0301 Triage Brief

## 请求
"下一步 pg 各个版本测试" —— 类比 T0300（MySQL 四版本逐版本转换测试），
对 PostgreSQL 各版本执行数据文件（heap + CLOG）物理直读→Parquet 的逐版本转换测试。

## 分类
- category: enhancement，scenario_type: development（产出脚本+全量对照测试，经 scenario-boundary-check 判定）

## Claim 勘察（事实）
- 现环境仅 t0216-pg 容器 = **PG18.4**（端口 5433, user=test, db=poct25），
  volume `c0100f11a03b.../_data`（/var/lib/postgresql）。
- poct25 库：poc_orders（**1M 行**，id/customer_id/amount numeric(12,2)/created_at/status/payload/active，
  与 MySQL poc_orders 同构）+ poc_orders_100m + poc_scen_v2/v3/v4 + poc_boundary。
- pgbin（build/pgbin）编译依据 `third_party/pg184/include`（PG18.4 头），
  t_infomask 等 heap 头字段**编译期访问**（pg_heap_reader.c:198），PG12+ 布局偏移 20。
- 版本差异矩阵（pg_versions.h，T0250 实测/逆向）：
  - t_infomask 偏移：PG12+ = 20；PG11 及更早 = 24（编译期头决定）
  - CLOG：PG10+ `pg_xact/`（pg_clog_reader_pg10.c 已实现）；PG9.x 及更早 `pg_clog/`
    （pg_clog_legacy_pg9.c **未实现占位恒 -1**）
  - SLRU 段（32 页/段）与 2-bit xid 状态编码各版本一致
- 本地镜像仅 postgres:latest（=18.4）；PG9.x/10/11 官方镜像需拉取（docker hub 有 postgres:9.6/10/11/12/...）。
- 无重复：T0250 仅单版本 PG18 直读 + AC-10 PG18 100M 回归；无 PG 多版本转换测试任务/知识。

## 待用户决策（P2 Grill）
1. 版本集：覆盖哪些 PG 版本（差异节点 = 9.x pg_clog / 10-11 偏移24 / 12+ 偏移20）
2. PG9.x pg_clog_legacy_pg9.c 是否实现（版本集含 9.x 则必须）
3. pgbin 多版本适配方式（按版本头编译多二进制 vs 运行时偏移适配）
4. 测试深度（全量逐字段对照 vs count/聚合级）
5. 数据源（pg_dump 迁移既有 1M vs 各容器独立灌数）
