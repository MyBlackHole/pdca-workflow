---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 本任务说明与状态索引：记录格式

本契约定义该记录的 schema、字段与填写约束。null、空列表和未验证状态表示事实尚未取得，
不构成授权、执行成功或资源取得证明。

## 示例

```markdown
---
schema: pdca.task/v4
protocol_revision: 4.0.0-rc.3
task_id: null
attempt: null
work_id: null
tree_revision: null
node_id: null
ontology_revision: null
ontology_object_refs: []
root_seed_ref: null
scene: null
title: null
phase: plan
execution_state: unexecuted
context_refs: []
parent_seed_ref: null
dependency_refs: []
writer: null
conversation_ref: null
baseline: null
last_transition: null
pending_request_ref: null
current_run_ref: null
project_context_ref: null
dispatch_ref: null
---

# 本任务说明与状态索引

字段保存 TASK-01 定义的 task/attempt 语义身份与当前状态导航；用户目标、node responsibility、
AC/oracle 等正文必须引用真实固定来源，不由父 Agent 代定。

普通 task 的 node/revision/scene/attempt 按 TASK-01 固定；root bootstrap 只使用 `root_seed_ref`
表达唯一例外。上下文选择只引用 CONTEXT-01 的结果，派发事实只引用 `dispatch_ref`，不在 task record
复制 assignment 或 dispatch 内容。

`phase` / `execution_state` 只保存 STATE-01 的派生投影，不是授权。恢复时从完整 transition、control、pending request/decision 与未决 operation 重新派生；`last_transition` / `current_run_ref` / `pending_request_ref` 只是导航指针。初始 `phase: plan` 不表示 Plan 已授权、Gate ready 或已经启动。
```
