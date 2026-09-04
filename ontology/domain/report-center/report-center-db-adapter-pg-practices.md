---
schema: pdca.asset/v1
id: ontology:domain/report-center-db-adapter-pg-practices
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/report-center-db-adapter-pg-practices/1.0.0
summary: Repository/Adapter 数据访问层 + PG 迁移 — 可复用实践
domain:
- ontology:domain/report-center
relations:
  specializes:
  - ontology:domain/report-center
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'Repository/Adapter 数据访问层' ontology/domain/report-center/report-center-db-adapter-pg-practices.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# Repository/Adapter 数据访问层 + PG 迁移 — 可复用实践

> 来源：T0216（Report DB 接口层与 PostgreSQL Adapter + Migrations），62 契约测试全绿（PG18.4 实测）。
> 关联：T0217 CLI 惰性导入知识、T0221 PG17 补验。

## 适用场景

构建"公共接口 + 单一数据库 Adapter"的分层数据访问层，且需要 Schema 迁移、
批量事务写入、Keyset 分页读取。本文件沉淀的是实现过程中收敛的**模式与坑位**，
供 T0218~T0222 及后续 DB 层任务复用。

## 核心模式

### 1. 迁移审计表保留策略（非标准做法，需自裁决）

问题：`down.sql` 若删除审计表 `rpt_schema_migration`，rollback 后无法再写 DOWN 审计；
若保留，`up.sql` 重新 `CREATE TABLE` 会 DuplicateTable。

解法：
- `down.sql` **不删除审计表**（rollback 后仍写 DOWN 审计）。
- `up.sql` 审计表用 `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS`。
- `rollback()` 成功后 **DELETE 对应 UP/SUCCESS 记录**，使重新 `migrate()` 能重建表。

要点：审计记录 `(version, checksum, direction, status)` 是迁移状态机的一部分，
"回滚 = 作废 UP 记录 + 追加 DOWN 审计"比"回滚 = 删表"更接近 Flyway 语义。

### 2. 空库首次迁移的审计表缺失容忍

`applied_versions()` 在首次迁移（审计表尚不存在）时查询会报 `UndefinedTable`。
解法：捕获 `psycopg.errors.UndefinedTable` 返回空集，视为空库。

### 3. 分区表主键必须写在父表

PostgreSQL 分区表的**主键约束必须定义在父表**，且必须包含分区键。
`CREATE TABLE dwd_task_run (...) PARTITION BY RANGE (task_time)` 若漏写
`PRIMARY KEY` 子句，子分区会继承不到主键，`ON CONFLICT (task_time, ...)` 报
`InvalidColumnReference: no unique or exclusion constraint matching`。

### 4. 逻辑字段名 → 物理列映射（QuerySpec/Keyset）

业务层用逻辑名（如 `entity_key`），物理表列名是 `data_source_key`/`host_key` 等。
- 维护 `_DIM_PK_COLUMN: {表名: 物理主键列}`。
- `_physical_column(field, table)`：`entity_key` 映射到该表物理主键列；公共字段直通；
  其余仅允许合法标识符。
- Keyset 分页排序/条件必须用**物理列**，且与 `SELECT ... ORDER BY` 一致。

### 5. 维度非公共列经 attribute 传入

维度表公共列统一（entity_key/backup_domain_id/source_table/...），非公共列
（如 `dim_host.data_source_key`）无独立字段。约定：**采集方把非公共列放进
`attribute` dict**，`_dim_rows` 写入时从 `attribute` 提取对应物理列，缺省用
`_DIM_EXTRA_DEFAULTS` 兜底。避免为每张表加专用字段污染公共接口。

### 6. 快照批次号统一填充（last_seen_batch_id）

资源快照对账靠 `last_seen_batch_id` 区分"本批次未见 → 标删除"。若记录由调用方
自行填充批次号，漏填会致对账误删。解法：`_seal_batch(records, batch_id)` 在写入前
用 `dataclasses.replace` 统一把 `snapshot.batch_id` 写入每条记录的 `last_seen_batch_id`。

### 7. SQLAlchemyJobStore DSN 驱动前缀

`postgresql://` 前缀被 SQLAlchemy 解析为 psycopg2 驱动（需额外安装）。统一转
`postgresql+psycopg://` 使用 psycopg v3，避免 psycopg2 依赖。

### 8. 测试隔离：自动迁移 + 清理测试分区

- conftest session 级：空库检测 `rpt_schema_migration` 是否存在，缺失则跑全部迁移。
- 每测试 TRUNCATE 业务表 + `DELETE FROM dwd_task_run` + 删除**非基线**分区
  （保留迁移内置的基线分区），保证测试幂等且不污染分区状态。

## 坑位清单

| 坑 | 症状 | 解法 |
|----|------|------|
| 迁移 base 切割错误 | "missing paired up/down" | `.up`/`.down` 后缀长度不同，用 `stem.rsplit(".",1)[0]` |
| 审计表被 down 删除 | rollback 后 migrate 无法重建 | down 保留审计表 + IF NOT EXISTS |
| 父表缺主键 | ON CONFLICT 无约束可匹配 | 主键定义在父表且含分区键 |
| 快照批次号漏填 | 对账误删 | `_seal_batch` 统一填充 |
| attribute 非公共列未提取 | NOT NULL 违反 | `_dim_rows` 从 attribute 提取 |
| Keyset 用逻辑字段排序 | entity_key 列不存在 | 物理列映射 |
| 连接上下文退出非 IDLE 回滚 | 写入被吞 | 改为 COMMIT |

## 验证方式

```bash
python3 -m pytest tests/ -q   # 62 passed（PG18.4 实测，全新库自动迁移）
python3 -m black report_center_db tests && python3 -m isort --profile black report_center_db tests
python3 -m compileall -q report_center_db
```
