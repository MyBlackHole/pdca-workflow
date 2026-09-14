---
schema: pdca.request/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
request_id: null
scope_kind: task
work_id: null
tree_revision: null
action: null
kind: phase_start
phase: null
run_id: null
subject_ref: null
subject_digest: null
conversation_ref: null
producer_ref: null
input_refs: []
created_at: null
---

# 当前阶段启动说明

明确本任务、场景、attempt及将启动的Plan／Do／Check／Act。展示目标、范围／非目标、固定输入及版本、预期真实产物、验收、写域、风险和未决问题。Act说明是否发布／沉淀。

用户批准前不执行目标阶段；可读必要上下文形成请求，不借此做建模或业务变更。上阶段结果与下阶段目标可一并呈现，避免重复盘问。

kind=clarification只问事实，不启动阶段。请求固定后不更改对象，同一请求不授权多run；多个待决对象的“同意”不可猜。确认内容保存为control/subjects/<request-id>.md不可变快照；request中的subject_ref/digest指向它，不指会更新的task.md，不自哈希。

工作级动作使用kind=work_action、scope_kind=work及work_id/tree_revision/action；task/attempt/phase/run留空，固定具名任务集／树清单。它不代替任何阶段的phase_start。
