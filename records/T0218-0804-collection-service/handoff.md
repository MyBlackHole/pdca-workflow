# T0218 handoff（跨会话桥接）

> 本记录只写跨会话交接信息，技术细节引用结论文档。

## 当前状态

- T0218（collection-service 调度采集入库服务）**Act 阶段**，verdict=confirmed（123 passed）。
- 任务即将归档；跟进任务 **T0223-0805-worker-adaptation** 已创建（挂 T0214 children），承接本任务已知限制。

## 未完成事项

- **T0223 适配层**（核心交接）：真实 Worker 注册进 JobHandlerRegistry（`register()` 当前全仓无调用点）、
  SQLAlchemy 版 TaskRepository（`increment_retry`/`update_status` 持久化）、Ingester 接入 report-center 入库事务。
- 大输出端到端测试：真实 channel 大 stdout 下 JSONL 熔断（256MiB）与 FILE_READY 边界。
- register-evidence.py 缺陷：同名 active entry 的 `--replace` 因 `matches[0]` 命中 superseded 旧条目失效，
  需修复为按 `superseded_by` 链取活条目。

## 已知约束

- RPyC `allow_pickle=True` + `allow_all_attrs=True`（app.py:69），仅绑 127.0.0.1，收紧留待适配层。
- APScheduler Job 函数必须模块级（SQLAlchemyJobStore 无法序列化实例方法）。
- rpyc 6.0.2 + Py3.14：错误归一化 `{ok, data|error}` + 客户端 `rpc_obtain()`。
- 独立 venv（PEP 668），依赖 rpyc/apscheduler/pyyaml/psycopg-pool。

## 推荐的下一步

1. 完成 T0218 归档（advance-phase → archive + 目录迁移）。
2. 启动 T0223 Plan：worker 工厂 + TaskRepository 持久化设计。

## 关键上下文文件列表

- `records/T0218-0804-collection-service/conclusion.md`（结论与下一轮建议）
- `records/T0218-0804-collection-service/evidence/`（e1-pytest-full-rev2.txt 等）
- `pdca/tasks/active/T0223-0805-worker-adaptation/task.json`（跟进任务）
- 实现仓库：`/home/black/Downloads/report-center/collection_service/`（scheduler/job_spec/rpc/workers）

## 建议加载技能

- `flow-plan`（T0223 Plan 阶段）
- `testing-strategy`（T0223 端到端测试设计）
- `secure-coding`（RPyC 契约收紧）
- `register-evidence`（convergence 证据登记，注意同名 replace 缺陷）
