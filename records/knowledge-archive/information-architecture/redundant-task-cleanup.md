---
schema: pdca.asset/v1
id: knowledge:information-architecture.redundant-task-cleanup
layer: knowledge
summary: 只清理无执行事实、无引用的 pending 任务占位，历史资产必须走归档保留
tags: [maintenance, cleanup, task-hygiene]
scenarios: [default]
phases: [plan, act]
applies_when: [任务列表包含未开始的临时占位]
excludes_when: [任务拥有 record、evidence、experience、knowledge 或 archive 历史]
source_ids: [experience:T0019--07-26-清理未开始的冗余任务占位]
confidence: high
status: active
---

# Pending Task Cleanup Rule

删除任务占位前必须同时满足：`status=pending`、没有 completed_at/record_id、没有 Evidence 或
Experience、没有外部引用。只满足“看起来旧”不能删除。

历史任务、records、knowledge、workspace、research 和 artifacts 属于可追溯资产，应通过正常
PDCA archive 或 migration 流程处理，不能用项目清理直接移除。
