# T0223 handoff（跨会话桥接）

> 本记录只写跨会话交接信息，技术细节引用结论文档。

## 当前状态

- T0223（collection-service worker 接线适配层）**Act 阶段**，verdict=confirmed（135 passed）。
- T0218 已知限制（Worker 未接线、真实 TaskRepository/Ingester 未实现）已闭合。
- 任务即将归档。

## 未完成事项

- 无必须跟进项。可选（conclusion 已记录，未建任务）：
  - RPyC `allow_pickle` 收紧（安全加固，独立任务）
  - 大输出 JSONL 熔断（256MiB）真实数据端到端验证
  - register-evidence.py 同名 active entry `--replace` 缺陷（`matches[0]` 命中 superseded 旧条目）——工具修复
- 真实 cdm-data-cli 输出的端到端验证（Ingester 行一致性）属 T0221 部署环境。

## 已知约束

- Ingester 维度行额外列必须并入 `attribute`（`_dim_rows` 从 attribute 取额外列，CLI 行字段在顶层）。
- task 行缺 `source_update_time` 抛 `SOURCE_UPDATE_TIME_MISSING`（非 KeyError 兜底）。
- Worker 绑定用 handler 闭包（`registry.register(topic, lambda spec, w=worker: w.run(spec.domain_id))`），签名贴合 scheduler 的 `registry.get(topic)(spec)`。

## 推荐的下一步

1. 完成 T0223 归档（advance-phase → archive + 目录迁移）。
2. 推进 T0219（report-web）或 T0220（templates）等 T0214 子任务。

## 关键上下文文件列表

- `records/T0223-0805-worker-adaptation/conclusion.md`（结论与已知限制）
- `records/T0223-0805-worker-adaptation/evidence/`（t0223-e1-rev2.txt 等）
- 实现仓库：`/home/black/Downloads/report-center/collection_service/workers/factory.py`、`workers/ingest.py`

## 建议加载技能

- `flow-plan`（后续 T0214 子任务 Plan）
- `secure-coding`（RPyC 契约收紧时）
- `testing-strategy`（大输出熔断测试设计）
