# T0223 PRD — collection-service worker 接线适配层

## 问题

T0218（collection-service）交付了调度/worker/JSONL/RPyC 核心，但真实 Worker 未接入
scheduler 运行链路、Ingester 未接 report-center 入库事务——调度触发时会抛
`JOB_SPEC_INVALID`（registry 未注册 handler）。T0218 conclusion 将此列为已知限制。

## 现状核实（Plan 阶段实测，修正 T0218 conclusion 假设）

**已确认可复用（T0216 已交付，T0218 误判为「未实现」）**：
- `PostgreSQLCollectionTaskRepository`（report_center_db/postgres/collection_task.py）
  完整实现 TaskRepository Protocol（create/update_status/increment_retry/get/
  running_tasks_for_domain），契约测试 test_collection_task_repo.py 已存在
- `PostgreSQLReportWriteRepository`（report_center_db/postgres/write.py:137）
  提供 write_resource_snapshot / upsert_task_batch / upsert_capacity

**真实缺口（3 项）**：
1. Worker 未注册：`JobHandlerRegistry.register()` 无调用点；scheduler 触发
   `registry.get(topic)` 抛 JOB_SPEC_INVALID
2. Ingester 未适配：workers 的 `Ingester` Protocol 无 report-center 实现
   （JSONL 行 → 领域对象转换缺失）
3. 端到端接线未验证：真实 repo/ingester + 真实 channel 大输出 JSONL 熔断边界

**CLI JSONL 行 schema（T0217 test_cli_contract.py 确认）**：
- resource: 1 行含 `data_source_key`（完整当前态快照维度/关系）
- task: 每任务 1 行含 `task_run_key`、`backup_domain_id`，需 `--cursor`
- capacity: 2 行（dim + fact），首行含 `storage_worker_name`
- collector 返回 `list[tuple[str, dict]]`（table 前缀 + 归一化业务行）

## 方案

- **Worker 注册**：handler 工厂闭包（P2 Grill 已确认方案 A）——装配点一次性构造
  真实 Worker（注入 task_repo/channel/ingester/temp_dir），
  `registry.register(topic, lambda spec: worker.run(spec.domain_id))`。
- **Ingester 适配**：新增 `PostgreSQLLineIngester`（workers 侧），实现
  `Ingester` Protocol：读 pending-ingest JSONL → 逐行 json.loads → 按 topic 分组
  映射为 ResourceSnapshot/TaskFact list/CapacitySnapshot → 调
  `PostgreSQLReportWriteRepository` 对应方法。入库失败抛可分类错误码
  （复用 report_center_db 的 pg 异常映射）。
- **TaskRepository 接线**：装配时直接注入 `PostgreSQLCollectionTaskRepository`，
  无需新实现。

## 用户故事

- 作为备份系统，域周期文件注册后，调度器按 interval 触发真实 Worker，采集数据经
  JSONL 落盘后由 Ingester 入库到 report-db，CollectionTask 状态全程持久化。
- 作为运维，入库失败时同 task_id 重试 1 次，retry_count 持久化到 rpt_collection_task。

## 实现决策

- Ingester 行解析器放在 collection_service 内（新文件 workers/ingest.py），依赖
  report_center_db 的 protocol.models 与 postgres.write（复用 T0216，不复制）。
- 错误码沿用 report_center_db.errors 的映射（RESOURCE_TRANSACTION_FAILED /
  INGEST_ADAPT_FAILED 等），不做新错误体系。
- 测试用 PG18.4（t0216-pg 容器）+ 既有 test_collection_task_repo 基础。

## 范围外

- RPyC `allow_pickle` 收紧（安全加固，另立任务）
- 大输出端到端熔断测试（256MiB 真实大数据）——仅做单元级熔断路径验证
- task 增量起点回补历史（遵循 T0218 现状：不回补）

## 验收标准

- [ ] AC-1: 三 Topic 真实 Worker 注册进 JobHandlerRegistry，装配点提供工厂函数；
  `registry.get(topic)(spec)` 能触发真实 Worker 的 run 流程
- [ ] AC-2: 真实 Ingester 将 pending-ingest JSONL 解析入库到 report-db（复用
  PostgreSQLReportWriteRepository），三 Topic 各覆盖；失败抛可分类错误码
- [ ] AC-3: CollectionTask 状态/retry/error 持久化到 rpt_collection_task（复用
  PostgreSQLCollectionTaskRepository），端到端断言入库前后行状态
- [ ] AC-4: 端到端测试验证「注册→触发→采集(fake channel)→JSONL→入库→状态持久化」
  闭环在 PG18.4 全绿（含入库失败重试 1 次路径）
