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

用户问题/目标、当前 node responsibility、范围/非目标、预期 output、AC/oracle、约束与当前待确认事项。
引用真实原消息，不由父 Agent 代定目标。

`ontology_revision + node_id + scene + attempt` 是任务语义身份的一部分。
`context_refs` 是 CONTEXT-01 选择出的具名必要输入，不是完整父上下文的快照；
`dependency_refs` 指向固定依赖交付/接口，不指向兄弟完整活动历史。

phase 初始 plan 不代表 Plan 已运行。每次依最后完整事件重建；
阶段完成保持最后 phase 并置 awaiting_confirmation。字段本身不产生批准。
```
