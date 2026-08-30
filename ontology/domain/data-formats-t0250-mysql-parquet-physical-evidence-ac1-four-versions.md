---
schema: pdca.asset/v1
id: ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions
type: domain
layer: Knowledge
status: active
summary: AC-1 MySQL 四版本 InnoDB .ibd 物理直读验证（5.6/5.7/8.0/8.4）
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

# AC-1 MySQL 四版本 InnoDB .ibd 物理直读验证（5.6/5.7/8.0/8.4）

## 环境
- 容器：t0250-mysql56(5.6.51, COMPACT) / t0250-mysql57(5.7.44, DYNAMIC) /
  t0250-mysql8(8.0, DYNAMIC) / t0250-mysql84(8.4.11, DYNAMIC)
- 灌数：`bench/gen_mysql_versions.py`（六表 CROSS JOIN 倍增 1M，无 WITH RECURSIVE，四版本通用）
- 快照：`mysqladmin shutdown`（innodb_fast_shutdown=0 全量刷盘）→ podman unshare 拷 .ibd
- 工具：build/mysqlbin（8.0+ SDI 驱动；5.6/5.7 无 SDI 走 `--schema=` CLI 参数化）

## 表
poc_orders 7 列：id BIGINT PK / customer_id INT / amount DECIMAL(12,2) /
created_at DATETIME(6) / status VARCHAR(16) / payload VARCHAR(96) / active TINYINT(1)

## 关键实现：CLI schema 参数化（5.6/5.7 无 SDI）
- SDI（data dictionary）8.0 才引入；5.6/5.7 表定义在 .frm，不在 .ibd
- mysqlbin 新增 `--schema=<file>`：`mysql_layout_from_schema_file()` 解析文本 schema
  构建 MysqlLayout（列序 = PK + DB_TRX_ID(6B) + DB_ROLL_PTR(7B) + 其余，与 SDI 布局一致）
- schema 格式（bench/poc_orders.schema）：
  id:bigint:pk / customer_id:int / amount:decimal(12,2) / created_at:datetime(6) /
  status:varchar(16) / payload:varchar(96) / active:bool
- 同时修复 max_rows 解析：argv[3] 被 `--schema=` 占用导致 rows=0，改 `--rows=` 显式参数

## 结果（四版本各 1M 行，物理直读 rows 全 = 1,000,000）

| 版本 | 行格式 | .ibd | 解析方式 | rows | leaf页 | 吞吐 |
|---|---|---|---|---|---|---|
| 5.6.51 | COMPACT | 192MB/12288页 | --schema | 1,000,000 | 10,076 | 636K/s |
| 5.7.44 | DYNAMIC | 192MB/12288页 | --schema | 1,000,000 | 10,076 | 302K/s |
| 8.0 | DYNAMIC | 138MB/8448页 | SDI | 1,000,000 | 7,693 | 937K/s |
| 8.4.11 | DYNAMIC | 192MB/12288页 | SDI | 1,000,000 | 10,119 | 389K/s |

## 聚合校验（parquet vs SQL，全版本一致）
| 指标 | 5.6 | 5.7 | 8.4 | SQL |
|---|---|---|---|---|
| count | 1,000,000 | 1,000,000 | 1,000,000 | 1,000,000 |
| SUM(amount) | 499,995,000.00 | 同 | 同 | 499,995,000.00 |
| distinct status | 4 | 4 | 4 | 4 (new/paid/shipped/closed) |
| active=true | 500,000 | 500,000 | 500,000 | 500,000 |
| id 范围 | 1~1,000,000 | 同 | 同 | 1~1,000,000 |

## 结论
AC-1 Pass：四版本 .ibd 物理直读原型全部解析成功，行数与 SQL count 一致（差异=0）。
5.6 COMPACT 与 5.7/8.0/8.4 DYNAMIC 行格式均在统一解析器下正确解码。
