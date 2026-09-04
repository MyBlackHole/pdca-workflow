---
schema: pdca.asset/v1
id: ontology:domain/data-formats-t0300-mysql-version-convert-test
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats-t0300-mysql-version-convert-test/1.0.0
summary: MySQL 多版本转换测试（T0300）— 逐版本 .ibd→Parquet 全量对照
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


# MySQL 多版本转换测试（T0300）— 逐版本 .ibd→Parquet 全量对照

适用场景：MySQL 多版本（5.6/5.7/8.0/8.4）逐版本 .ibd→Parquet 转换测试、
版本特性拆分后的回归验证、数据文件转换产物正确性校验。

## 核心结论
- 四版本（5.6.51 COMPACT / 5.7.44 DYNAMIC / 8.0 DYNAMIC / 8.4.11 DYNAMIC）
  各 1M 行 .ibd→Parquet 转换 rows 均=1,000,000，parquet 与 SQL 全量逐字段对照差异=0，
  聚合（count / SUM(amount) / distinct status / active=true / id 范围）全一致。
- 版本特性拆分（mysql_sdi_80.c / mysql_layout_schema_56_57.c / 统一页解析）在四版本上无回归。

## 关键陷阱：输出页序 ≠ 主键序
- mysqlbin 按**物理页序**（B+树叶子页在表空间分配顺序）输出记录，
  **不保证主键序**：5.6/5.7/8.4 实测页序≠id 序，8.0 恰好一致（偶然）。
- 顺序敏感消费 mysqlbin 输出前，必须先按主键列排序；
  内容校验应顺序无关（按主键映射逐行对照）。

## 测试流程模板（可复用）
1. **数据提取**（`bench/extract_version_ibd.sh`）：
   `SET GLOBAL innodb_fast_shutdown=0` → 容器内 `mysqladmin shutdown`（全量刷盘）→
   `podman unshare` 拷贝 volume 内 .ibd → **unshare 内 `chown 0:0`**（命名空间根 = 宿主调用者；
   用 `chown $(id -u)` 会因 uid 映射落到 100999 宿主侧不可读）。
2. **转换**：8.0/8.4 走 SDI 自动布局（无 --schema）；5.6/5.7 无 SDI 走 `--schema=bench/poc_orders.schema`。
3. **SQL 基准**：`podman exec <c> mysql -N -B -e "SELECT ... ORDER BY id"` 全量导出（容器运行期，与干净关闭快照数据一致）。
4. **全量对照**（`bench/verify_version_convert.py`）：parquet 按 id 排序 vs SQL 逐行逐字段
   规范化文本对照（amount 定长 2 位 / created_at DATETIME(6) 文本 / active 0/1 / NULL="NULL"）
   + 行数 + 聚合三路验证。

## 工具
- `bench/extract_version_ibd.sh`：容器 volume .ibd 干净提取（容器名/volume hash/版本映射显式声明）。
- `bench/verify_version_convert.py <ver> <parquet> <sql_tsv>`：三路验证，差异=0 且聚合一致即 PASS（exit 0）。

## 注意
- 多实例并行转换会争用 CPU，吞吐不可作为基准（单实例基准见 T0250 AC-5）。
- 测试数据（.ibd / *_sql.tsv / *.parquet）不入 git 与 pdca，仅在证据记录中登记引用。
