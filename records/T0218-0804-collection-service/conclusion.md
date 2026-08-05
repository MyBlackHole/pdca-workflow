---
schema: pdca.asset/v1
id: T0218-0804-collection-service
phase: check
source_ids: [e1-pytest-full-rev2, e2-code-scale-rev2, convergence-map]
---

## 上下文

T0218 实现 collection-service 调度采集入库服务（主方案 subscheme），承接 T0214/T0216
的 report-db 与 PG 适配层。范围：三 Topic（resource/task/capacity）Job 调度与防重入、
11 类失败处理、重启恢复、JSONL 校验入库、RPyC 契约（§2.2 通用 Job 方法）。
Plan 阶段已确认：独立 venv（rpyc 6.0.2 / apscheduler 3.11.3 / psycopg-pool / pyyaml），
PG18.4 容器（T0216 62 项回归作为基准），场景类型 development。

## 假设与结果

| 假设 | 结果 |
|------|------|
| APScheduler JobStore 可持久化 Job 函数 | **推翻**：实例方法含 scheduler 无法序列化 → Job 必须模块级 `run_job` + `_scheduler_registry` 查实例（scheduler.py:81） |
| RPyC 异常可跨进程原样重抛 | **推翻**：rpyc 6.0.2 + Py3.14 对 netref 的 dunder `__name__` 访问在 pytest assert 重写中触发远程拒绝 → 服务端错误归一化 `{ok, data\|error}` + 客户端 `rpc_obtain()`（rpc/client.py） |
| apscheduler 3.11 事件类为 JobErrorEvent/JobMissedEvent | **推翻**：实际为 `JobExecutionEvent`/`JobSubmissionEvent`（scheduler.py:212） |
| apscheduler pending 状态 add_job 按 id 去重 | **推翻**：未 start 时 add_job 只进 pending 不去重 → 幂等依赖 `_specs` 记录 |
| Py3.14 重复 `mkdir(parents=True)` 幂等 | **推翻**：重复调用抛 FileExistsError → 需 `exist_ok=True` |

## 分析

**AC-1~AC-9 全部满足**（123 passed，含 T0216 62 项 PG 回归）：
- AC-1 文件锁互斥（filelock.py StartupLock，spawn 跨进程测试）
- AC-2 三 Topic 注册 + 同域同 topic 防重入（_specs 记录幂等）
- AC-3 RPyC 通用 Job 10 方法（add/adds/modify/pause/resume/remove/get_job(s)+
  ensure/remove_domain_schedule_config）；周期唯一来自域周期文件，add_job 拒绝
  Client 触发器（JOB_SPEC_INVALID）；job_id 契约 `{topic}:{domain_id}` 与
  handler_code（resource_collect 等）分离
- AC-4 状态机 COLLECTING→EXECUTING→FILE_READY→INGESTING→SUCCESS（base.py）
- AC-5 JSONL receiving→pending-ingest + 熔断（1MiB 行 / 64-256MiB 文件）
- AC-6 11 类失败分类；入库失败仅重试 1 次（_ingest_with_retry + increment_retry）
- AC-7 重启恢复（recovery.py 清目录 + 未终态置 FAILED）
- AC-8 task 增量起点（after_key_provider）+ cursor_overlap
- AC-9 密码脱敏（channel.py redaction）

**Check 阶段补齐**：AC-3 通用 Job 方法（初版仅 4 个调度方法）与 AC-6 入库重试
（初版无重试）为 Do 交付后的实质缺口，Ch1 逐条核对时发现并补全，+9 测试。

## 失败原因（仅 rejected/partial）

N/A（结论 confirmed）。

## 适用边界

- **已知限制（Grill 确认，属后续适配层跟进任务）**：
  1. 真实 Worker（TaskWorker/ResourceWorker/CapacityWorker）未接入 scheduler 运行
     链路——`JobHandlerRegistry.register()` 无调用点，scheduler 触发时
     `registry.get(topic)` 抛 JOB_SPEC_INVALID；真实 TaskRepository（含
     increment_retry 持久化）与 Ingester 仅 Protocol/Fake，无 SQLAlchemy 实现。
     本任务 AC-4/6/7 的单元契约由 Fake 验证满足；worker→scheduler→RPyC 完整接线
     与真实 repo/ingester 适配留待独立跟进任务。
  2. 安全 trade-off：RPyC `allow_pickle=True` + `allow_all_attrs=True`
     （app.py:69）。仅绑 127.0.0.1 无网络暴露，同机可信进程调用；收紧（移除
     allow_pickle）留待适配层契约类型约束工作。
- **测试覆盖边界**：JSONL 熔断路径（max_file_bytes 256MiB）未在真实 channel
  大输出下验证，仅单元测试覆盖 writer 熔断逻辑；真实 CLI 通道未端到端联测。
- 系统 Python 受 PEP 668 保护，依赖隔离于独立 venv，不污染系统环境。

## 下一轮建议

- **新建跟进任务（worker 接线适配层）**：真实 Worker 注册进 JobHandlerRegistry
  （handler 工厂绑定 repo/channel/temp_dir）、SQLAlchemy 版 TaskRepository
  （update_status/increment_retry 持久化到 report-db）、Ingester 接 report-center
  入库事务。挂 T0214 children，与 T0219（report-web）并行。conclusion 早期版本
  误写「T0219 适配层」，T0219 实为 report-web 登录鉴权，不承担本接线。
- 大输出端到端测试：真实 channel 大 stdout 下 JSONL 熔断与 FILE_READY 边界。
- register-evidence 缺陷：同名 active entry 的 `--replace` 因 matches[0] 命中
  superseded 旧条目而失效，建议修复为按 superseded_by 链取活条目。
