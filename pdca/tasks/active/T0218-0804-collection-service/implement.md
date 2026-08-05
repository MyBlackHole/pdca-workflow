# T0218 collection-service 实现顺序

## 前置

- T0216 Report DB Adapter（已完成，report-center 同仓）
- T0217 cdm-data-cli（已完成，aio-cdm 仓）
- T0215 Collection Service 子方案（唯一契约源）
- report-center venv：`.venv/`（rpyc 6.0.2 / apscheduler 3.11.3 / psycopg-pool）

## D1 基础设施

1. pyproject.toml 追加 `rpyc>=6.0` 依赖；`collection_service/` 包骨架。
2. `errors.py`：11 类错误码枚举 + 领域异常。
3. `filelock.py`：fcntl 文件锁（可注入路径，测试用临时文件）。
4. 验证：test_filelock（双实例阻止）。

## D2 域周期文件配置

5. `config.py`：加载 `collection-jobs.d/<domain_id>.yaml`，校验三 Topic
   interval_minutes/max_schedule_delay_seconds，非法即拒绝，不回退默认。
6. 验证：test_scheduler_jobs（缺失/非法/额外键拒绝）。

## D3 调度器 + Job 契约

7. `job_spec.py`：JobSpec dataclass + JobHandlerRegistry（resource/task/capacity_collect）。
8. `scheduler.py`：CollectionScheduler（BackgroundScheduler + SQLAlchemyJobStore +
   事件监听 + 防重入 add_job 封装）。
9. 验证：test_scheduler_jobs（60/5/10 注册、replace_existing、max_instances 防重入）。

## D4 RPyC 服务/客户端

10. `rpc/service.py`：CollectionSchedulerRPCService 10 方法，非法参数拒绝 JOB_SPEC_INVALID；
    ensure/remove_domain_schedule_config（域校验 + 原子复制域周期文件）。
11. `rpc/client.py` + `rpc/decorators.py`：Client + remove_session_after_running。
12. 验证：test_rpc_job_contract（真实 Client/Service 本机端口）。

## D5 JSONL 状态机 + 熔断

13. `jsonl.py`：receiving 写入/逐行校验/原子改名/熔断（1MiB 行、256/64MiB 文件）/字节统计。
14. 验证：test_jsonl（校验通过/失败/熔断）。

## D6 Worker（三 Topic）

15. `workers/base.py`：TopicWorker 基类（状态机、失败分类、文件生命周期、入库重试 1 次）。
16. `workers/resource_worker.py` / `task_worker.py` / `capacity_worker.py`。
17. `channel.py`：ChannelClient（mock rpc 工具进程调用 cdm-data-cli，--password 脱敏）。
18. 验证：test_workers_*（三 Topic 语义、11 类失败、task 增量起点、重试）。

## D7 重启恢复 + 应用入口

19. `recovery.py`：未终态→FAILED/WORKER_RECOVERED、清目录、JobStore 恢复。
20. `app.py`：start_safe() 编排（文件锁→调度器→RPyC→事件监听→恢复）。
21. 验证：test_app_start_safe + test_recovery（时序）。

## D8 收尾

22. 全量 `.venv/bin/python -m pytest tests/ -q`（PG18.4 实测）；black/isort/compileall。
23. Z1~Z4：register-evidence → convergence → git commit（report-center + pdca-workflow）→ do→check。

## 验证命令

```bash
cd /home/black/Downloads/report-center
./.venv/bin/python -m pytest tests/ -q
./.venv/bin/python -m black collection_service tests
./.venv/bin/python -m isort --profile black collection_service tests
./.venv/bin/python -m compileall -q collection_service
```

## 已知限制（登记 evidence）

1. RPyC 6.0.2 venv 安装（PEP 668 系统环境隔离）；不污染系统 Python。
2. 域周期文件权限/路径属生产部署（T0221）；本环境校验内容与逻辑。
3. CDM 通道以 mock rpc 工具进程模拟；真实 CDM 集成归 T0221/T0217 生产接线。
