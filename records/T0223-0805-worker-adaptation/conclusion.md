---
schema: pdca.asset/v1
id: T0223-0805-worker-adaptation
phase: check
source_ids: [e1-pytest-full-rev2, convergence-map-rev2]
---

## 上下文

T0223 承接 T0218 conclusion 已知限制：真实 Worker 未接入 scheduler 运行链路、
Ingester 未接 report-center 入库事务。Plan 阶段核实后显著缩小范围——T0216 已交付
`PostgreSQLCollectionTaskRepository`（TaskRepository Protocol 完整实现）与
`PostgreSQLReportWriteRepository`（三 Topic 入库能力），T0218 误判「真实
TaskRepository 未实现」不成立。真实缺口仅剩 Worker 注册 + Ingester 适配。

## 假设与结果

| 假设 | 结果 |
|------|------|
| T0216 已提供真实 TaskRepository 可复用 | **成立**（Plan 核实，T0218 conclusion 误判已修正） |
| Worker 用 handler 工厂闭包绑定（方案 A） | **成立**（Grill 确认；registry.get(topic)(spec) 触发 worker.run(domain_id)） |
| Ingester 需 JSONL 行 → 领域对象转换（CLI 行 schema 与领域对象字段有差异） | **成立**（resource 行 source_table 分发 + task 字段映射 + capacity dim/fact 区分） |
| 维度行额外列在顶层而非 attribute | **推翻初版**：`_dim_rows` 从 attribute 取额外列 → 需把行顶层字段并入 attribute（实测 dim_data_source_name 为空暴露） |
| task 缺 source_update_time 由 write.py 校验 | **修正**：Ingester 构造 TaskFact 前先校验，抛 SOURCE_UPDATE_TIME_MISSING（避免 KeyError→REPORT_DB_FAILED） |

## 分析

**AC-1~AC-4 全部满足**（135 passed，含 T0218 基线 123 + T0223 新增 12）：
- AC-1 Worker 注册：factory.py `build_worker_registry` 三 Topic 真实 Worker 注册，
  handler 闭包绑定；S1 测试验证注册 + registry.get(topic)(spec) 触发 resource/task
- AC-2 Ingester 入库：ingest.py `PostgreSQLLineIngester` 三 Topic JSONL→对象分发
  （ResourceSnapshot/TaskFact/CapacitySnapshot）→ write.py 入库；错误码
  JSONL_INVALID / SOURCE_UPDATE_TIME_MISSING / TASK_PARTITION_SPAN_EXCEEDED /
  RESOURCE_TRANSACTION_FAILED / REPORT_DB_FAILED
- AC-3 状态持久化：S3 e2e 用真实 PostgreSQLCollectionTaskRepository，PG 断言
  rpt_collection_task status=SUCCESS / retry_count
- AC-4 端到端闭环：S3 e2e（PG18.4）「注册→触发→采集(fake channel)→JSONL→入库→
  状态持久化」全绿，含入库失败重试 1 次（FlakyWriter → retry_count=1）

**关键工程决策**：
- 复用 T0216 两个 repository，零新 SQL——Ingester 仅做 JSONL→对象转换适配
- dimension 行额外列并入 attribute（对齐 `_dim_rows` 消费方式）
- 错误码沿用 T0218 errors.py 体系，report_center_db 异常经 _map_reportdb_error 映射

## 失败原因（仅 rejected/partial）

N/A（结论 confirmed）。

## 适用边界

- **已知限制（Grill 确认）**：Ingester 的 JSONL 行以 T0217 test_cli_contract 为契约
  基准（S2/S3 测试行手工构造对齐），未用真实 cdm-data-cli 输出验证——真实 CDM 主机
  端到端属 T0221 部署环境验证。
- **组合覆盖**：task/capacity 的端到端入库 = S2 解析（已验证）+ test_write_repo
  真实入库（已验证），非单测试直通，但组合覆盖成立。
- e2e 仅覆盖 resource 主题全程（task/capacity 需分区表准备，由 test_write_repo 既有
  覆盖），非缺项。
- RPyC allow_pickle 安全收紧、大输出 JSONL 熔断（256MiB 真实大数据）仍为 T0218/T0223
  范围外（未纳入，另立任务）。

## 下一轮建议

- 无必须跟进项（T0223 完整闭环）。可选项：
  - RPyC 契约收紧（allow_pickle 移除）作为安全加固独立任务
  - 大输出端到端 JSONL 熔断（256MiB）真实数据验证
  - register-evidence 同名 active entry 的 --replace 缺陷（matches[0] 命中 superseded）
    修复为按 superseded_by 链取活条目（T0218 已记录，未修复）
