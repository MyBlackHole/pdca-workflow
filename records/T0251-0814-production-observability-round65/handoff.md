## 当前状态

T0251 已完成 Check，用户 verdict 为 `confirmed`，Act 产物已写入，待执行 `act -> archive`。结构化日志、JSONL/file sink、轮转、关键备份事件和 Make/CMake/TLS 全回归均有 evidence。

## 未完成事项

`TreeCheckpoint::confirmed` 仍是按路径增长的内存 map；T0251 的 100k 恢复证据只证明语义，不证明海量 RSS。T0252 已在 Plan，尚未获得该轮最终方案确认，不得进入 Do。

## 已知约束

- 当前主机没有暴露 `MDB_VL32` 的 LMDB header/library；no-mmap 分支由 T0250 独立跟进。
- checkpoint 远端 ACK、journal fsync、SQLite index commit 的顺序必须保留 crash-safe/duplicate-safe 语义。
- 目标是生产级海量文件，不得用关闭 checkpoint、mmap 或全量重传规避内存问题。

## 推荐的下一步

1. 对 T0252 的 SQLite disk B-tree + append journal + bounded pending 方案完成用户终审。
2. 进入 Do，抽取 `src/tree_checkpoint.cpp`，实现流式迁移、坏尾截断、replay offset、point lookup 和故障注入。
3. 跑 100k/1M 三次中位数 benchmark，独立报告 RSS、CPU、恢复吞吐、skip/resent/duplicate-safe 指标。

## 关键上下文文件列表

- `/home/black/Documents/pdca-workflow/records/T0251-0814-production-observability-round65/conclusion.md`
- `/home/black/Documents/pdca-workflow/knowledge/observability/structured-logging-jsonl-rotation.md`
- `/home/black/Documents/pdca-workflow/pdca/tasks/0814-tree-checkpoint-paged-round66/prd.md`
- `/home/black/Documents/pdca-workflow/pdca/tasks/0814-tree-checkpoint-paged-round66/design.md`
- `/home/black/Downloads/backupstream/src/backupctl.cpp`

## Suggested skills

- `flow-plan` / `flow-do` / `flow-check` / `flow-act`
- `grilling`
- `domain-modeling-work`
- `register-evidence`
- `write-journal`
