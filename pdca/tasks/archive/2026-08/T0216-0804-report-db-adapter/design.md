# T0216 Report DB 接口层与 PostgreSQL Adapter — 设计

## 架构

落地 `/home/black/Downloads/report-center` 新仓库。顶层包名 `report_center_db`：

```text
report-center/
  pyproject.toml
  report_center_db/
    __init__.py
    config.py            # 配置加载：连接串/池/超时，仅适配器初始化层使用
    protocol/
      __init__.py
      interfaces.py      # 全部公共 Protocol 接口
      models.py          # 领域记录（dataclass），不含驱动类型
      query.py           # QuerySpec / KeysetCursor / 分页
      capabilities.py    # DatabaseCapabilities
    postgres/
      connection.py      # PostgreSQLConnectionFactory
      transaction.py     # PostgreSQLTransactionManager
      read.py            # PostgreSQLReportReadRepository
      write.py           # PostgreSQLReportWriteRepository
      preference.py      # PostgreSQLReportPreferenceRepository
      user.py            # PostgreSQLReportUserRepository
      collection_task.py # PostgreSQLCollectionTaskRepository
      jobstore.py        # PostgreSQLSchedulerJobStoreFactory
      migrations.py      # PostgreSQLMigrationAdapter
      errors.py          # PG 错误码 → 领域错误映射
      dialect.py         # 方言 SQL / 参数绑定
    migration/
      runner.py          # 迁移执行器：校验、事务、审计、回退
      manager.py         # 幂等 admin 引导（依赖 user repo）
    read.py              # 只读工具函数（内部）
  migrations/postgresql/
    V001__init.up.sql
    V001__init.down.sql
  tests/
    conftest.py          # PG 连接 fixture（本机 PG18.4）
    test_connection.py
    test_transaction.py
    test_read_repo.py
    test_write_repo.py
    test_preference_repo.py
    test_user_repo.py
    test_collection_task_repo.py
    test_jobstore_factory.py
    test_migrations.py
```

## 接口契约（§3.4）

全部公共接口为 `typing.Protocol`；返回值为 `models.py` 领域 dataclass。禁止在接口/模型/QuerySpec 中暴露 psycopg、SQLAlchemy 类型或方言 SQL。

| 接口 | 职责 |
|------|------|
| `ReportDatabaseConnectionFactory` | 读/写/Export/Metric 受限连接池上下文、健康检查；连接失效销毁不归还 |
| `ReportTransactionManager` | 只读/读写事务边界、提交、回滚 |
| `ReportReadRepository` | 只接收 `QuerySpec`+域权限+分页游标；任务增量游标读取 |
| `ReportWriteRepository` | 资源快照（整文件单事务+对账）、任务批次 Upsert+聚合重建、容量批次 |
| `ReportPreferenceRepository` | Token 有效期读写；已保存报告 CRUD+模糊搜索（owner 固定传入） |
| `ReportUserRepository` | 按用户名查有效用户、密码哈希/首改密标记读写、幂等创建 admin |
| `CollectionTaskRepository` | `rpt_collection_task` 创建与状态流转 |
| `SchedulerJobStoreFactory` | 创建 APScheduler `SQLAlchemyJobStore` |

`DatabaseCapabilities`：事务、Upsert、行级锁、Keyset、时间类型，全部由 PG Adapter 声明 true。

## 迁移系统（§3.5.1）

- 命名统一 **`V001__init`**（§3.5.1 目录约定为准；§3.5.5 的 `0001_initial_report_schema` 视为叙述性名称，不产生第二套命名）。
- `V001__init.up.sql` 建全部一期表；`down.sql` 成对逆序删除。
- `rpt_schema_migration` 审计：执行前计算 up/down 脚本 SHA-256，成功写 `SUCCESS/UP(DOWN)`，失败回滚并写 `FAILED/UP`。单版本事务内执行。
- 执行器校验：配对文件存在、checksum 与发布清单一致、已成功版本 up 未被改写（记录在 rpt_schema_migration）。

## 表基线（V001__init）

控制表：`rpt_backup_domain`、`rpt_report_user`、`rpt_system_setting`、`rpt_saved_report`、`rpt_collection_task`、`rpt_schema_migration`。

维度 8 张：`dim_data_source`、`dim_host`、`dim_backup_unit`、`dim_backup_object`、`dim_instance`、`dim_protection_object`、`dim_policy`、`dim_storage_worker`。公共字段含 `entity_key 主键`、`backup_domain_id`、`source_table/source_id`、`source_create/update_time`、`attribute JSONB`、`last_seen_batch_id`、`is_deleted`、`etl_create/update_time`，`UNIQUE(backup_domain_id, source_table, source_id)`，`CHECK(source_table ~ '^[a-z0-9_]+$')`、`CHECK(source_id >= 0)`、`CHECK(<entity>_key = backup_domain_id::text || ':' || source_table || ':' || source_id::text)`。外键均 `ON DELETE RESTRICT`。

复合外键（§3.5.2）：`dim_host`/`dim_backup_unit`/`dim_protection_object` 的 `(backup_domain_id, data_source_key) → dim_data_source`。`dim_backup_object.data_source_key` 按主方案原文为单列 FK。

关系 2 张：`rel_protection_instance(protection_object_key, instance_key)`、`rel_protection_policy(protection_object_key, stage_key)`，含 `backup_domain_id/last_seen_batch_id/is_deleted/etl_*`。

事实：`dwd_task_run`（周分区父表，`PRIMARY KEY(task_time, backup_domain_id, task_run_key)`，索引 `idx_task_domain_cursor`、`idx_task_domain_run_key`、`idx_task_domain_source_update_cursor`、`idx_task_domain_scene_status_time`、`idx_task_etl_update_brin`）+ 当前/下一周基线分区；`dwd_storage_worker_capacity_daily`（普通表，`PRIMARY KEY(stat_date, backup_domain_id, storage_worker_key)`）。

聚合：`agg_task_daily`（`PRIMARY KEY(stat_date, backup_domain_id, db_type, task_scene, task_type)`）。

`apscheduler_jobs` 由 SQLAlchemyJobStore 自动建，不入 V001。

## 分区（§3.5.5）

- `V001__init` 建分区父表 + 当前周、下一周基线分区（含本地索引）。
- `PostgreSQLReportWriteRepository.ensure_task_time_partitions(week_starts)`：运行期按需建缺失周分区，单批次最多 260；超限在任何 DDL/写入前抛 `TASK_PARTITION_SPAN_EXCEEDED`，不建部分分区、不写部分事实。
- `dwd_storage_worker_capacity_daily`、`agg_task_daily` 不分区。

## 原子性（§7/§7.1）

- 资源快照：整文件单事务；`last_seen_batch_id = resource_batch_id(task_id)`；同事务对账 `last_seen_batch_id != resource_batch_id` 且有效 → `is_deleted=true`；文件校验/任何失败禁止对账；不物理删除。
- 任务：`(backup_domain_id, task_run_key)` 入库前批量预查旧值（定位冻结 `task_time` 分区 + 取旧盖章值）；按 `(task_time, backup_domain_id, task_run_key)` 幂等 Upsert；缺 `source_update_time` → `FAILED/SOURCE_UPDATE_TIME_MISSING`。
- 任务聚合：同事务内受影响切片 `backup_domain_id+stat_date+task_scene+task_type`（新值∪旧值并集）先删后按 `db_type` 分组重建。
- 容量：先 Upsert 维度再写事实（可同事务）；同日同 Worker 直接覆盖，无 `collection_time` 新旧比较；不因列表缺失删除 Worker。
- 任务/容量批次短事务（非整文件）。

## 错误码映射

- PG 错误（连接拒绝、唯一冲突、deadlock、事务中止等）→ 领域错误；`TASK_PARTITION_SPAN_EXCEEDED`、`SOURCE_UPDATE_TIME_MISSING` 为业务错误。
- 连接失效销毁，不归还池。

## 测试策略（AC-1~AC-7）

- 契约测试跑本机 PG18.4（`tests/conftest.py` 从环境变量读连接串，默认 `postgresql://test:test@127.0.0.1:5433/report_test`）；PG17 留 T0221 补验（已 grill 确认）。
- AC-2 迁移：up 后表清单/索引/约束校验 + `rpt_schema_migration` 审计；down 成对；改写 up 拒绝。
- AC-3 分区：基线分区存在；`ensure_task_time_partitions` 建缺失周、260 上限抛错、不建部分。
- AC-4 快照：单事务提交含对账；失败回滚无残留；缺批次不标记删除。
- AC-5 幂等：重复 Upsert 不产生重复事实；预查旧值用于聚合重建。
- AC-6 契约测试 PG18 实测通过。
- AC-7 接口不泄露驱动类型（类型注解检查）。
- `SchedulerJobStoreFactory` 冒烟：创建 jobstore、add/get/remove job。
