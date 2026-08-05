# Report DB 接口层与 PostgreSQL 17 Adapter + Migrations — 规格文档

## 问题陈述

报表中心需以 Repository/Adapter 模式访问独立 Report DB（一期唯一实现 PostgreSQL 17）。当前无任何实现：控制表、资源维度/关系、任务/容量事实、任务日聚合、Schema 迁移、APScheduler JobStore 均需建立。

## 解决方案

实现代码层公共接口（`ReportDatabaseConnectionFactory`/`ReportTransactionManager`/`ReportReadRepository`/`ReportWriteRepository`/`ReportPreferenceRepository`/`ReportUserRepository`/`CollectionTaskRepository`/`SchedulerJobStoreFactory`）+ PostgreSQL 17 Adapter 实现 + 成对迁移脚本（`V001__init` 起，含 `rpt_schema_migration` 审计）。

## Seam 分析

- 测试接缝：公共接口契约测试（同一契约测 PG17 实现）、Migration Adapter 执行 up/down 并校验 SHA-256、`DatabaseCapabilities` 声明。
- Mock/Stub：外部依赖为 PostgreSQL 17 实例；用测试库 + 契约 seed fixture 隔离。

## 用户故事

1. 作为 collection-service 实现者，我想要 Write Repository 批量事务 Upsert，以便资源快照/任务/容量原子入库。
2. 作为 report-web 实现者，我想要 Read Repository Keyset 分页与权限域过滤，以便固定模板查询。

## 实现决策

- 落地仓库：**report-center 新仓库**（`/home/black/Downloads/report-center`，已 git init）。
- 技术栈：Python 3.14 + **psycopg v3（同步）** 公共接口 Adapter；APScheduler `SQLAlchemyJobStore`（SQLAlchemy 2.0）供 `SchedulerJobStoreFactory` 使用；迁移用原生 SQL + `rpt_schema_migration` 审计。
- 测试环境：本机 PostgreSQL 18.4（podman 容器 `t0216-pg`，127.0.0.1:5433，库 `report_test`）；PG17 镜像拉取网络超时，**AC-6 调整为本环境 PG18 实测 + PG17 生产验证（T0221 部署时补验）**。
- 依赖契约：T0215（Collection Service 子方案、Web API 子方案中 DB 相关部分）。
- 表范围（主方案 §3.5）：`rpt_backup_domain`、`rpt_report_user`、`rpt_system_setting`、`rpt_saved_report`、`rpt_collection_task`、`rpt_schema_migration`、`dim_*` 8 张、`rel_protection_instance`/`rel_protection_policy`、`dwd_task_run`（周分区父表+基线分区）、`dwd_storage_worker_capacity_daily`、`agg_task_daily`。
- 禁止 `ON DELETE CASCADE`；公共字段/entity_key CHECK/复合外键按 §3.5.2/3.5.3。
- 迁移版本成对 `up.sql`/`down.sql`，SHA-256 校验，事务内执行。

## 测试决策

- Repository 契约测试（正/负/边界）、migration up/down 冒烟、`rpt_schema_migration` 审计、PG17 连接池/事务回滚。

## 验收标准

- [ ] AC-1: 公共接口与 PostgreSQL 17 Adapter 全部实现，业务代码仅依赖接口（§3.4）。
- [ ] AC-2: 迁移脚本 `V001__init` 起成对 up/down，`rpt_schema_migration` 记录版本/checksum/direction/status（§3.5.1）。
- [ ] AC-3: `dwd_task_run` 创建分区父表 + 当前/下一周基线分区，`ensure_task_time_partitions` 运行期建分区、单批次上限 260、超限 `TASK_PARTITION_SPAN_EXCEEDED`（§3.5.5）。
- [ ] AC-4: 资源快照整文件单事务 + 缺失对账逻辑删除同事务提交（§7.1）。
- [ ] AC-5: 任务事实 `(task_time, backup_domain_id, task_run_key)` 主键幂等 Upsert，批量预查旧值用于聚合重建（§7、§3.5.6）。
- [ ] AC-6: 契约测试在本机 PG18.4 实测通过；其他数据库不实现、不宣称支持（§3.4.2）；PG17 于 T0221 部署时补验。
- [ ] AC-7: 全部 Repository 方法不泄露驱动/方言类型；连接失效销毁不归还池（§3.4）。

## 范围外

- 不实现达梦/金仓/GaussDB Adapter。
- 不做容量性能压测（归 T0222）。

## 备注

- 依赖：T0215；下游：T0218、T0219、T0220、T0221。
