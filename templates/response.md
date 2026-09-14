---
schema: pdca.response/v4
protocol_revision: 4.0.0-rc.1
task_id: null
attempt: null
request_id: null
scope_kind: task
work_id: null
kind: null
phase: null
run_id: null
subject_ref: null
subject_digest: null
response: null
source_ref: null
actor_ref: null
conversation_ref: null
host_received_event_ref: null
recorded_at: null
---

# 用户真实回应副本

保留可核实的原生消息ID／transcript、用户actor、原始文字及当前显示对象。confirmed/rejected/needs_change/clarification_answer不互换。

执行Agent可抄录真实消息，但不能认证自己生成的批准，不能用父Agent转述或source:user标签冒充原始用户来源。摘要不认证身份；无法核对保持等待。时间未知留空，不倒填。
