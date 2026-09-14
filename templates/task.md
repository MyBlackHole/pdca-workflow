---
schema: pdca.task/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
work_id: null
tree_revision: null
node_id: null
scene: null
title: null
phase: plan
execution_state: unexecuted
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

用户问题／目标、范围／非目标、成功标准、约束、当前待确认事项。引用真实原消息，不由父Agent代定目标。

phase初始plan不代表Plan已运行。每次依最后完整事件重建；阶段完成保持最后phase并置awaiting_confirmation。pending_request_ref指向具体下一动作；自身字段不产生批准。
