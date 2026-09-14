---
schema: pdca.control-event/v1
event_id: null
scope_kind: null
work_id: null
task_id: null
attempt: null
kind: null
control_revision: null
previous_event_ref: null
previous_event_digest: null
source_ref: null
policy_ref: null
request_id: null
subject_digest: null
host_order_receipt_ref: null
observed_last_transition_ref: null
observed_last_transition_digest: null
inflight_operation_refs: []
capability_check_refs: []
reservation_refs: []
recorded_at: null
time_source_ref: null
protocol_revision: 3.4.11
---

# 控制事件草稿

只有可信宿主控制写入者能提交有效事件；Agent可提出请求但不能自造用户来源。kind如stop_requested/capability_lost/capability_restored/record_handoff/terminated/request_decided。工作scope无task，任务scope必须绑定task/attempt；事件序号与PDCA的1—4分开。

## 事实与动作

记录实际来源、影响范围、停止哪些新增动作、在途清单、真实后端结果和不确定性。source为fixture时必须明确测试身份，不用于生产授权。控制时间只有真实计时依据，不倒填。

## 写入与恢复

先提交不可变事件再更新control/runtime视图。Agent还持有task写权时宿主不同时改task；控制准入先阻止动作，随后真实交回/撤权后封存。部分事件只作异常，不解释为已停止。
