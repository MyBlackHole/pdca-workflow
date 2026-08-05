# T0216 implement.md — 实现顺序与验证

## 依赖与工具

- Python 3.14.6（本机）；psycopg 3.3.4、SQLAlchemy 2.0.51、APScheduler 3.11.3、pytest 9.0.3 已装。
- PG 测试库：本机 PG18.4 容器 `t0216-pg`，`postgresql://test:test@127.0.0.1:5433/report_test`。
- 代码格式化：black + isort（--profile black），与 CI 一致；`python3 -m compileall` 校验。

## 实现顺序（Do 阶段）

### D1 骨架 + V001 迁移
1. `git init` 已完成；写 `pyproject.toml`（包名 `report_center_db`，py>=3.10，依赖 psycopg[binary]>=3.2、sqlalchemy>=2.0、apscheduler>=3.10）。
2. 写 `migrations/postgresql/V001__init.up.sql` / `down.sql`：
   - up：`pg_trgm` 扩展、`rpt_*` 控制表、8 张 `dim_*`、2 张 `rel_*`、`dwd_task_run` 分区父表 + 当前/下周基线分区、`dwd_storage_worker_capacity_daily`、`agg_task_daily`、全部索引/CHECK/复合外键。
   - down：按依赖逆序 DROP TABLE。
3. 迁移执行器 `migration/runner.py` + `postgres/migrations.py`（校验配对、SHA-256、单版本事务、`rpt_schema_migration` 审计）。
4. 验证：跑 `test_migrations.py`（up→审计→down→审计→表消失）。

### D2 协议接口 + 模型
5. `protocol/interfaces.py` 定义 8 个 Protocol；`protocol/models.py` 领域 dataclass；`protocol/query.py` QuerySpec/KeysetCursor；`protocol/capabilities.py`。
6. 验证：接口无驱动类型泄漏（`test_interface_purity.py` 静态扫描注解 + mypy 风格断言）。

### D3 连接/事务
7. `postgres/connection.py`、`transaction.py`、`errors.py`、`dialect.py`（连接池、失效销毁、错误映射）。
8. 验证：`test_connection.py`（健康检查、错误连接销毁、池复用）、`test_transaction.py`（提交/回滚/嵌套只读）。

### D4 写入 Repository（核心业务）
9. `write.py`：资源快照（整文件事务 + `ensure_task_time_partitions` 内联 + 对账）、任务批次 Upsert + 预查 + 聚合重建、容量批次。
10. 验证：`test_write_repo.py`（AC-3 分区 260 上限、AC-4 快照对账、AC-5 幂等 + 聚合重建）。

### D5 读取/偏好/用户/采集任务/JobStore
11. `read.py`（QuerySpec + Keyset + 域权限 + 任务增量游标）、`preference.py`、`user.py`、`collection_task.py`、`jobstore.py`。
12. 验证：对应契约测试 + `test_jobstore_factory.py`（add/get/remove job 冒烟）。

### D6 收尾
13. 全量 `pytest tests/ -q`（PG18.4 实测，AC-6）；black/isort 格式化；`compileall`。
14. Z1~Z4：register-evidence → convergence → git commit（report-center 仓库 + pdca-workflow）→ do→check。

## 验证命令

```bash
cd /home/black/Downloads/report-center
python3 -m pytest tests/ -q                 # 全量（依赖 PG18.4 容器）
python3 -m pytest tests/test_migrations.py -q
python3 -m black report_center_db tests && python3 -m isort --profile black report_center_db tests
python3 -m compileall -q report_center_db
```

## 已知限制（登记 evidence）

1. 实测为 PG18.4；PG17 差异留 T0221 生产部署补验（已 grill 确认）。
2. `dim_backup_object.data_source_key` 按主方案原文为单列 FK（不额外改复合 FK）。
3. `0001_initial_report_schema` 与 `V001__init` 命名统一为后者（design.md 已裁决）。
