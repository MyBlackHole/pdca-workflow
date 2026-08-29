---
schema: pdca.asset/v1
id: ontology:concept/pdca-task
type: concept
layer: Knowledge
summary: PDCA 任务元概念
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-task

PDCA 任务元概念：一个完整 PDCA 周期的载体。

- **含义**：由 `task.json` 跟踪 `meta.phase` / `status` / 各类标记；阶段只能经 `transition-phase.py` 按 `pdca-transition` 合法边推进。
- **关键不变量**：`final_confirmation` / `check_confirmation` 不可由 AI 代签；阶段推进须经门禁校验。

