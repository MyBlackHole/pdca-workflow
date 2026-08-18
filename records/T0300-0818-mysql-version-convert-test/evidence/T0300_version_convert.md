# T0300 MySQL 四版本逐版本 .ibd→Parquet 转换测试（5.6/5.7/8.0/8.4）

## 范围
逐版本执行完整转换（.ibd→Parquet）+ 全量逐字段对照（parquet vs SQL 基准）+ 聚合对照，
并补齐 T0250 AC-1 聚合校验表缺失的 8.0 列。覆盖版本拆分后的解析路径：
`mysql_sdi_80.c`（8.0/8.4 SDI）、`mysql_layout_schema_56_57.c`（5.6/5.7 --schema）、
`mysql_parse_pages.c`（统一页/行解析）。

## 数据
- 来源：既有容器 volume（t0250-mysql56/57/8/84 内 poct25.poc_orders，各 1M 行），未重灌
- 提取：`bench/extract_version_ibd.sh`（innodb_fast_shutdown=0 干净关闭 → podman unshare 拷 .ibd）
- SQL 基准：`podman exec <c> mysql -N -B -e "SELECT ... ORDER BY id"` 全量 1M 行导出

## 工具
- 转换：build/mysqlbin（8.0+/8.4 走 SDI 自动布局；5.6/5.7 无 SDI 走 `--schema=bench/poc_orders.schema`）
- 对照：`bench/verify_version_convert.py`（parquet 按 id 排序后与 SQL 逐行逐字段规范化文本对照，
  行数 + 全量 7 列 + 聚合三路验证）

## 结果

| 版本 | 行格式 | .ibd | 解析方式 | rows | 全量逐字段差异 | 聚合对照 | 吞吐(并行争用)* |
|---|---|---|---|---|---|---|---|
| 5.6.51 | COMPACT | 201MB | --schema | 1,000,000 | 0 | PASS | 277K/s |
| 5.7.44 | DYNAMIC | 201MB | --schema | 1,000,000 | 0 | PASS | 277K/s |
| 8.0 | DYNAMIC | 138MB | SDI | 1,000,000 | 0 | PASS | 277K/s |
| 8.4.11 | DYNAMIC | 201MB | SDI | 1,000,000 | 0 | PASS | 275K/s |

\* 本测试四实例并行执行共享 CPU，吞吐低于 AC-1 单实例基准（636K/302K/937K/389K/s），非回归。

## 聚合对照（parquet vs SQL，全量 1M 行，补齐 8.0 列）
| 指标 | 5.6 | 5.7 | 8.0 | 8.4 | SQL |
|---|---|---|---|---|---|
| count | 1,000,000 | 1,000,000 | 1,000,000 | 1,000,000 | 1,000,000 |
| SUM(amount) | 499,995,000.00 | 同 | 同 | 同 | 499,995,000.00 |
| distinct status | 4 | 4 | 4 | 4 | 4 (new/paid/shipped/closed) |
| active=true | 500,000 | 500,000 | 500,000 | 500,000 | 500,000 |
| id 范围 | 1~1,000,000 | 同 | 同 | 同 | 1~1,000,000 |

## 重要发现
- mysqlbin 按**物理页序**输出，不保证与主键序一致：56/57/84 页序≠id 序，8.0 恰好一致。
  对照脚本以 id 为键排序后逐行比对，实现顺序无关的全量校验（内容一致性不受物理序影响）。

## 结论
四版本转换测试全 PASS：rows=1M、全量逐字段差异=0、聚合对照一致。
版本拆分（SDI/legacy schema/统一解析）在四版本上无回归，逐版本转换产物与 SQL 基准完全一致。
