---
schema: pdca.asset/v1
id: T0216-0804-report-db-adapter
phase: check
source_ids: [e1-pytest-full-revised, e2-code-scale, e3-migrations, convergence-map]
---

## 上下文

T0214 决策落地 T0216：Report Center 需以 Repository/Adapter 模式访问独立 Report DB，
一期唯一实现 PostgreSQL。创建独立新仓库 `/home/black/Downloads/report-center`
（用户 grill 决策，非 aio-cdm）。实现 8 个公共 Protocol（connection factory /
transaction manager / read / write / preference / user / collection task / jobstore factory）
+ PG Adapter + `V001__init` 成对迁移（含 `rpt_schema_migration` 审计）。
主方案 §3.4/§3.5/§7 为契约唯一事实源。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 公共接口不泄漏驱动/方言类型（AC-1/AC-7） | ✅ test_interface_purity 5 项静态扫描通过 |
| 迁移成对 up/down + 审计 + 改写拒绝（AC-2） | ✅ 7 项测试；rollback 作废 UP 记录、审计表保留（自裁决） |
| 分区父表主键 + 260 上限 + 超限抛错（AC-3） | ✅ 基线分区 20260803/20260810 + 建缺失 + `TaskPartitionSpanExceededError` |
| 快照整文件单事务 + 缺失对账（AC-4） | ✅ 单事务/缺批次标记/恢复/失败回滚 4 项测试 |
| 任务主键幂等 Upsert + 预查聚合重建（AC-5） | ✅ 同 key 同 task_time 覆盖不重复、缺 source_update_time 拒绝、聚合重建+db_type 变化清理 |
| 本机 PG18.4 契约实测（AC-6） | ✅ 62 测试全绿（全新库自动迁移）；PG17 留 T0221 补验 |
| SchedulerJobStore 可用（AC 辅助） | ✅ DSN 转 `postgresql+psycopg`，APScheduler 端到端冒烟通过 |

## 分析

1. **根因链排查**（Do 阶段收敛 62 全绿）：初轮 37 failed → 62 passed。主要根因：
   (a) `dwd_task_run` 分区父表缺主键子句（补 `(task_time,backup_domain_id,task_run_key)`）；
   (b) `runner.py` 版本配对 base 切割错误（`.up`/`.down` 长度不同 → 用 `rsplit`）；
   (c) 空库首次迁移 `applied_versions` 查审计表报 UndefinedTable（容忍返回空集）；
   (d) rollback 后审计表仍标 UP/SUCCESS 导致 migrate 跳过（rollback 作废 UP 记录）；
   (e) 快照批次号未统一填充 `last_seen_batch_id` 致对账误删（`_seal_batch`）；
   (f) dim 非公共列（`dim_host.data_source_key`）无法写入（`_dim_rows` 从 attribute 提取）；
   (g) QuerySpec 逻辑字段 `entity_key` 未映射物理主键列（`_physical_column`）；
   (h) JobStore DSN 默认 psycopg2 驱动（转 `postgresql+psycopg`）。
2. **审计表保留策略（自裁决）**：down.sql 不删除 `rpt_schema_migration`，保证 rollback
   后仍写 DOWN 审计；`rollback()` 成功后 DELETE 对应 UP/SUCCESS 记录使迁移可重建。
   与标准迁移工具（如 Flyway）行为一致，已登记 evidence。
3. **测试隔离**：conftest session 级自动迁移 + 每测试 TRUNCATE + 清理非基线分区，
   保证全新库 / 顺序执行均幂等。

## 适用边界

- 实测环境 PG18.4；PG17 差异（分区/语法/psycopg 行为）留 T0221 生产部署补验。
- `dim_backup_object.data_source_key` 按主方案原文单列 FK，未改复合 FK（design.md 已裁决）。
- 容量/任务侧不做性能压测（归 T0222）。
- 连接池参数 `min_size=1, max_size=5` 为测试默认，生产按负载调整。

## 下一轮建议

1. T0221（生产部署）：PG17 环境补验迁移与契约测试，关闭 AC-6 剩余项。
2. T0218/T0219/T0220：接入 read/write/preference/user/collection 接口实现业务功能。
3. 生产连接池与调度 JobStore 配置按部署拓扑校准。
