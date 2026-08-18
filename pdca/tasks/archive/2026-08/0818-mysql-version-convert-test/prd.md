# MySQL 四版本每个版本的转换测试（.ibd→Parquet 逐版本验证）— 规格文档

## 问题陈述

- **现状**: T0250 已验证 MySQL 5.6/5.7/8.0/8.4 四版本 .ibd 可解析（rows=1M 一致），但聚合校验表缺 8.0 列、四版本转换产物（parquet）未逐版本保留、验证未组织为"每个版本一个转换测试记录"。POC 源码已按版本特性拆分文件（mysql_sdi_80.c / mysql_layout_schema_56_57.c 等），但拆分后的解析逻辑未做逐版本回归。
- **目标**: 对 5.6/5.7/8.0/8.4 每个版本各执行一次完整的 .ibd→Parquet 转换测试，产物与验证记录逐版本保留，并补 8.0 聚合缺口；同时回归验证版本特性拆分后的 mysqlbin。
- **差距**: 无逐版本转换测试记录与产物；8.0 聚合对照缺失；版本拆分后无全量回归。

## 解决方案

- 数据：四版本容器 volume 内已有 poct25.poc_orders（1M 行/版本），用 podman unshare 提取 .ibd 到 evidence/mysql/versions/<ver>/。
- 转换：`build/mysqlbin <ver>.ibd <ver>.parquet`（8.0+ SDI；5.6/5.7 加 `--schema=bench/poc_orders.schema`）。
- 对照基准：各版本容器启动后 `mysql -N -B -e "SELECT ..."` 导出全量 SQL 文本（id,customer_id,amount,created_at,status,payload,active）。
- 全量对照：python（pyarrow）读每版本 parquet，行按统一序列化（amount→固定2位小数字符串、created_at→DATETIME(6) 文本、active→0/1），与 SQL 导出逐字段全量比对（1M×7×4）。
- 补 8.0 聚合：与其余版本同口径（count/SUM/distinct/active/range）。
- 记录：每版本转换测试结果 + 对照摘要写入 evidence/mysql/versions/ 下独立 md；汇总写入 manifest.jsonl。

## Seam 分析

### 测试接缝
- 边界：mysqlbin（.ibd→parquet 命令行工具）输出契约 = rows、列值；对照脚本以 parquet 文件为被测接口，SQL 导出为外部基准（容器内 mysql 客户端，隔离于被测进程）。
- 已有覆盖：T0250 AC-1 解析验证（1M rows）、AC-8 LOB 验证；本轮新增全量逐字段对照。
- Mock/Stub：SQL 基准来自容器内真实 mysqld（不 mock）；比对脚本只依赖 parquet 文件 + 文本基准，无网络依赖。

### 声明的测试接缝
- seam: bench/verify_version_convert.py -> src/mysql/mysql_parse_pages.c
- seam: bench/verify_version_convert.py -> src/mysql/mysql_sdi_80.c
- seam: bench/verify_version_convert.py -> src/mysql/mysql_layout_schema_56_57.c
- seam: bench/extract_version_ibd.sh -> /home/black/.local/share/containers/storage/volumes/*/_data

### 验收可测性
- 每个 AC 有明确 pass/fail（对照差异数=0）。
- 边界：5.6/5.7 无 SDI（schema 路径）、8.0/8.4 SDI（自动布局）——由版本差异矩阵覆盖。

## 用户故事

1. 作为数据迁移工程师，我想要四版本每个版本的 .ibd→Parquet 转换测试记录，以便确认 mysqlbin 在目标版本上的正确性。
2. 作为测试负责人，我想要全量 1M 行逐字段对照，以便获得比聚合更强的转换正确性证据。
3. 作为维护者，我想要版本特性拆分后的源码回归通过，以便确认拆分未引入回归。

## 实现决策

- 不修改 POC 解析源码（本轮仅测试）；若对照暴露缺陷，走 Do 阶段修复并记录。
- 产物目录：evidence/mysql/versions/{56,57,80,84}/（ibd + parquet + 对照结果 md + SQL 基准）。
- 脚本：bench/extract_version_ibd.sh（unshare 提取）、bench/verify_version_convert.py（全量对照）。
- 时间成本：4×1M 转换（秒级）+ 4×1M 全量比对（python 流式/内存集合，预估分钟级）+ SQL 导出（容器内）。
- SQL 基准序列化格式与 parquet 端统一（见解决方案）。

## 测试决策

- 全量逐字段对照为唯一通过标准（差异数=0）。
- 聚合校验（count/SUM/distinct/active/range）作为附加上下文记录。
- 失败判定：任何字段差异 > 0 即该版本转换测试不通过，记录差异样本。

## 验收标准

- [ ] AC-1: 四版本 .ibd 均成功提取至 evidence/mysql/versions/<ver>/（5.6/5.7/8.0/8.4）
- [ ] AC-2: 每版本 mysqlbin 转换成功（8.0/8.4 SDI 自动布局；5.6/5.7 --schema=），rows 均 = 1,000,000
- [ ] AC-3: 每版本 parquet 与 SQL 全量逐字段对照差异数 = 0（1M×7 列，含 8.0）
- [ ] AC-4: 8.0 聚合口径补齐（count/SUM(amount)/distinct status/active=true/id 范围）并与 SQL 一致
- [ ] AC-5: 每版本转换测试记录（md）写入 evidence/mysql/versions/<ver>/，manifest.jsonl 登记四版本转换产物与对照摘要
- [ ] AC-6: 版本特性拆分（mysql_sdi_80.c / mysql_layout_schema_56_57.c / mysql_lob_read_8013.c）未引入回归（AC-2/AC-3 通过即证）