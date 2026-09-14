---
schema: pdca.request-decision/v1
decision_id: null
scope_kind: null
work_id: null
tree_revision: null
proposal_id: null
task_id: null
attempt: null
request_id: null
request_digest: null
kind: null
phase: null
conversation_ref: null
subject_ref: null
subject_digest: null
terminal_state: null
response: null
response_ref: null
source_ref: null
policy_ref: null
deadline: null
decision_time: null
time_source_ref: null
previous_control_ref: null
control_revision: null
backend_order_receipt_ref: null
protocol_revision: 3.4.11
---

# 请求唯一终局草稿

CONTROL-01定义pending只转一次：consumed/expired/cancelled/superseded。consumed需要真实响应及身份/对象/期限通过；response=confirmed才可能支持阶段批准，其他响应不批准。expired不需要伪造用户source，而应引用已授权policy和实际时钟依据。

任务scope的task/attempt/phase/conversation全匹配；work scope使用work/tree/proposal与工作会话、subject=manifest，无task/phase。不交叉消费。

决策时间由同一可信宿主提交边界产生，deadline严格小于比较；不能用客户端发送时间追认过期消息。同一决策重复返回原记录，冲突保留并阻断。任务后续取消可使已批准请求不再允许新的动作，不能把consumed当永久执行权。
