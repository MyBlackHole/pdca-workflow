---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 本任务说明与状态索引：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
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
```
