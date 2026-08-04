# collection-service 调度采集入库服务 — 规格文档

## 问题陈述

采集调度核心服务缺失：需实现单实例 APScheduler 周期调度、固定 Topic Worker、经既有 rpc 工具通道调用 `cdm-data-cli`、本地 JSONL 接收/校验/入库、任务状态流转、失败处理与重启恢复。

## 解决方案

实现 `collection-service`：`start_safe()`（文件锁单实例）→ `BackgroundScheduler` + `SQLAlchemyJobStore` → 50 线程采集池 → resource/task/capacity 固定 Worker → RPC 通道 Client（`collect(task_id, topic, after_key)`）→ 本地 JSONL（receiving→pending-ingest）→ 校验 + 批量事务 Upsert → `rpt_collection_task` 状态机；`CollectionSchedulerRPCService`（RPyC）提供通用 Job 管理与受限周期文件方法。

## Seam 分析

- 测试接缝：Job 注册/暂停/删除（RPyC Client/Service 契约）、`max_instances=1` 防重入、JSONL 校验（逐行/字节熔断）、11 类失败路径、重启恢复（未终态任务置 `FAILED/WORKER_RECOVERED` + 清目录 + JobStore 恢复）。
- Mock/Stub：CDM 侧通道以 mock rpc 工具进程模拟；JobStore 用真实 SQLAlchemyJobStore（PG17 测试库）。

## 用户故事

1. 作为运维，我想要采集失败可查（`rpt_collection_task`），以便只读账号排障。
2. 作为调度控制者，我想要通用 Job 管理与防重入，以便同一 (域, Topic) 不并发采集。

## 实现决策

- 落地仓库：**report-center 新仓库**。
- 依赖：T0215（Collection Service 子方案）、T0216（Repository/JobStore）、T0217（CLI）。
- 固定 Job ID `resource/task/capacity:{domain_id}`，`add_job` 服务端生成 interval 触发器（周期唯一来自域周期文件，拒绝 Client 传入触发器；§4.2.1）。
- 线程池固定 50，`max_instances=1`，调度线程不执行采集（§4.1）。
- 失败处理 11 类 + RTO（§6.4）；仅入库失败同 task_id 重试 1 次（§5.1、§6.4.1）。
- 重启恢复按 §6.3.1；资源快照原子事务与缺失对账同事务（§7.1）。

## 测试决策

- RPyC Job 契约测试、防重入并发测试、JSONL 完整性/熔断测试、11 类失败场景、重启恢复时序、入库幂等重试测试。

## 验收标准

- [ ] AC-1: `start_safe()` 以文件锁阻止第二个实例；RPyC `ThreadedServer` 后台线程运行（§2.1、§4.1）。
- [ ] AC-2: 三 Topic 周期 Job 注册（60/5/10 分钟），周期唯一来自域周期文件，缺失/非法拒绝注册；`max_instances=1` 同域同 Topic 防重入（§4.2、§4.3）。
- [ ] AC-3: `add_job`/`add_jobs`/`modify_job`/`pause_job`/`resume_job`/`remove_job`/`get_job(s)`/`ensure_domain_schedule_config`/`remove_domain_schedule_config` 行为与 §4.2.1 表一致，Client 传入触发器/周期/任意 Callable 被拒。
- [ ] AC-4: 每次采集先建 `rpt_collection_task` 再发起调用；状态按 `COLLECTING→EXECUTING→FILE_READY→INGESTING→SUCCESS/FAILED` 推进（§3.2）。
- [ ] AC-5: JSONL 接收写入 `receiving`，退出码 0 且逐行校验通过后原子改名 `pending-ingest`；单行/单文件字节熔断 `JSONL_SIZE_LIMIT_EXCEEDED`（§6.2）。
- [ ] AC-6: 11 类失败处理路径（§6.4）全部实现；仅入库失败同 task_id 重试 1 次，`retry_count` 正确；RTO 达标（5/10/60 分钟）。
- [ ] AC-7: 重启时未终态任务置 `FAILED/WORKER_RECOVERED`，清空本地目录，从 JobStore 恢复 Job；不恢复旧 RPC 流/旧文件（§6.3.1）。
- [ ] AC-8: `task` Topic 增量起点 = 本域 `dwd_task_run` 最大 `source_update_time` 回退 `cursor_overlap_seconds`（默认 60s），不落独立 cursor 表（§3.2、§6.2）。
- [ ] AC-9: 通道 RPC 密码参数在日志脱敏；无 CDM 数据库连接串/直连权限（§1、§3.1.1）。

## 范围外

- 不做告警/Metric/Watchdog 服务。
- 不做首次全量状态机/断点续传。

## 备注

- 依赖：T0215、T0216、T0217；下游：T0219（Job 控制 RPC 调用方）、T0221、T0222。
