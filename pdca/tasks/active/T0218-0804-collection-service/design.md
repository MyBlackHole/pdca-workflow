# T0218 collection-service 调度采集入库服务 — 设计

## 架构

落地 `/home/black/Downloads/report-center` 仓库（T0216 同仓）。新增包 `collection_service`：

```text
report-center/
  pyproject.toml          # 追加 rpyc>=6.0 依赖
  collection_service/
    __init__.py
    app.py                # start_safe() 入口：文件锁→调度器→RPyC→事件监听→恢复
    scheduler.py          # CollectionScheduler：BackgroundScheduler + SQLAlchemyJobStore + 事件
    job_spec.py           # JobSpec / handler_code 枚举 / JobHandlerRegistry
    rpc/
      service.py          # CollectionSchedulerRPCService（RPyC 暴露）
      client.py           # CollectionSchedulerRPCClient（report-web 用）
      decorators.py       # remove_session_after_running
    workers/
      base.py             # TopicWorker 基类：状态机、失败分类、文件生命周期
      resource_worker.py  # resource_collect（60min，快照+对账）
      task_worker.py      # task_collect（5min，增量+聚合重建）
      capacity_worker.py  # capacity_collect（10min，容量样本）
    channel.py            # ChannelClient：经既有 rpc 工具通道调用 cdm-data-cli
    jsonl.py              # JSONL 接收/校验/熔断/原子改名/字节统计
    recovery.py           # 重启恢复：未终态→FAILED/WORKER_RECOVERED、清目录、JobStore 恢复
    config.py             # 域周期文件加载/校验（collection-jobs.d/<id>.yaml）
    filelock.py           # 文件锁（fcntl）
    errors.py             # 领域错误码（11 类）
  tests/
    test_app_start_safe.py
    test_scheduler_jobs.py
    test_rpc_job_contract.py
    test_workers_*.py
    test_jsonl.py
    test_recovery.py
    test_filelock.py
```

## 关键设计决策

### D1. 调度架构（§2.1/§2.2/§4.1）

- `BackgroundScheduler` 含 `SQLAlchemyJobStore`（T0216 `PostgreSQLSchedulerJobStoreFactory`）。
- 调度线程不执行采集；固定 50 线程池（`ThreadPoolExecutor`）执行 Worker。
- Job ID `resource/task/capacity:{domain_id}`；`max_instances=1`、`coalesce=true`、
  `replace_existing=true`。
- APScheduler 事件监听 `EVENT_JOB_EXECUTED|EVENT_JOB_ERROR`：成功提交 / 异常回滚。

### D2. RPyC 契约（§2.2）

- RPyC 6.0.2（venv 安装）。`ThreadedServer` 后台线程，`allow_all_attrs=True`、
  `allow_pickle=True`，默认 `127.0.0.1:8889`。
- `handler_code` 仅取 `JobHandlerRegistry` 注册值（`resource_collect`/`task_collect`/
  `capacity_collect`）；Client 传 Callable/触发器/周期/`next_run_time` 一律 `JOB_SPEC_INVALID`。
- 方法集：`add_job`/`add_jobs`/`modify_job`/`pause_job`/`resume_job`/`remove_job`/
  `get_job`/`get_jobs`/`ensure_domain_schedule_config`/`remove_domain_schedule_config`。
- 修改型方法用 `remove_session_after_running` 装饰器清理会话。

### D3. 域周期文件（§2.3）

- `conf/collection-jobs.d/<domain_id>.yaml`：仅 `resource/task/capacity` 三 Topic 的
  `interval_minutes` + `max_schedule_delay_seconds`。默认 60/5/10 分钟，延迟上限
  3600/300/600 秒。缺失/非法/含其他键/域 ID 不匹配即拒绝注册；**绝不回退全局默认**。

### D4. Worker 流程（§3）

- 每次采集先建 `rpt_collection_task`（T0216 CollectionTask 接口），再读配置调 RPC。
- 状态机：`COLLECTING→EXECUTING→FILE_READY→INGESTING→SUCCESS/FAILED`。
- 资源：快照 Upsert + 对账同事务（`write_resource_snapshot`）。
- 任务：`dwd_task_run` 最大 `source_update_time` 回退 60s 为增量起点（不落 cursor 表）；
  Upsert + 聚合重建。
- 容量：Worker 维度 Upsert + 同日覆盖样本；0 记录只写维度。

### D5. 失败处理（§6.4，11 类）

| 分类 | error_code | 处理 |
|------|-----------|------|
| 1 调度/本地准备 | DOMAIN_DISABLED/DUPLICATE_RUN/SCHEDULE_DELAY_EXCEEDED/TASK_WATERMARK_READ_FAILED | FAILED，不发 RPC 不建文件 |
| 2 RPC 建连 | RPC_CONNECT_FAILED | FAILED，关 Client |
| 3 RPC 受控采集 | TOPIC_UNSUPPORTED/RPC_ARGUMENT_INVALID/CLI_START_FAILED/CLI_AUTH_FAILED | FAILED，记受限 stderr |
| 4 源端执行 | SOURCE_DB_CONNECT_FAILED/SOURCE_DB_AUTH_FAILED/SOURCE_QUERY_TIMEOUT/SOURCE_QUERY_FAILED/CLI_EXEC_FAILED | FAILED，删接收文件 |
| 5 通道异常/超时 | RPC_WAIT_TIMEOUT/RPC_CONNECTION_BROKEN/RPC_CHANNEL_UNAVAILABLE | 关 Client，删文件，FAILED |
| 6 本地写失败 | LOCAL_FILE_WRITE_FAILED | 关 Client，删文件，FAILED |
| 7 JSONL 校验 | JSONL_INVALID/JSONL_SIZE_LIMIT_EXCEEDED/SOURCE_UPDATE_TIME_MISSING | 删文件，FAILED |
| 8 分区超限 | TASK_PARTITION_SPAN_EXCEEDED | DDL/业务写入前失败 |
| 9 重启恢复 | WORKER_RECOVERED | 启动清目录 + 未终态 FAILED |
| 10 入库失败 | INGEST_ADAPT_FAILED/REPORT_DB_FAILED/RESOURCE_TRANSACTION_FAILED | 同 task_id 重试 1 次；资源失败禁止对账 |
| 11 删文件失败 | LOCAL_FILE_DELETE_FAILED | 保持 SUCCESS，只补删 |

### D6. 重启恢复（§6.3.1）

启动顺序：查询未终态 → `FAILED/WORKER_RECOVERED` → 清空固定 JSONL 目录 →
幂等清理已删域周期文件 → 加载校验域周期文件与全局执行参数 → 从 JobStore 恢复 Job。
不复用旧 task_id/旧文件/旧 RPC 流。

### D7. JSONL 状态机（§5）

- `{task_id}.receiving.jsonl` → 校验（退出码 0 + 逐行 JSON）→ 原子改名
  `{task_id}.pending-ingest.jsonl` → 校验 + 批量事务 Upsert → SUCCESS → 删除文件。
- 熔断：`max_line_bytes`（1 MiB）、`max_file_bytes`（resource 256MiB / task、capacity 64MiB）。
- 固定 `collection_temp_dir` 唯一落点；禁止其他目录。

### D8. 文件锁（§2.1）

`start_safe()`：`fcntl.flock` 独占锁 `/opt/aio/report_center/run/apscheduler.lock`
（测试用临时路径），获取失败即退出并提示第二实例。

## 测试策略（AC-1~AC-9）

- AC-1 文件锁：双实例并发，第二个 start_safe 返回未启动。
- AC-2 三 Topic Job 注册：60/5/10 分钟；周期唯一来自域文件；非法拒绝；
  max_instances=1 防重入（并发 double-run 断言单执行）。
- AC-3 RPyC 契约：方法行为 + 非法参数（触发器/周期/Callable）拒绝（JOB_SPEC_INVALID）。
- AC-4 状态机：全流程 COLLECTING→...→SUCCESS/FAILED；rpt_collection_task 记录校验。
- AC-5 JSONL：接收/校验/原子改名/熔断（行/字节）；JSONL_SIZE_LIMIT_EXCEEDED。
- AC-6 11 类失败：每类 error_code + 重试 1 次（retry_count）+ RTO 断言。
- AC-7 重启恢复：未终态→FAILED/WORKER_RECOVERED；目录清空；JobStore 恢复。
- AC-8 task 增量：最大 source_update_time 回退 60s；不落 cursor 表。
- AC-9 脱敏：日志 --password → ***；无 CDM 直连。

测试接缝：JobStore 用真实 SQLAlchemyJobStore（PG18.4 测试库，T0221 补 PG17）；
CDM 侧通道以 mock rpc 工具进程模拟；RPyC 契约用真实 Client/Service（本机端口）。

## 已知限制

1. RPyC 6.0.2 与本机系统 Python 不兼容的 PEP 668 问题通过 report-center venv 解决
   （用户 grill 决策）。
2. 域周期文件权限 0640/0750 属生产部署配置（T0221），本环境仅校验内容与路径。
3. 50 线程池为固定值（§4.1）；压测归 T0222。
