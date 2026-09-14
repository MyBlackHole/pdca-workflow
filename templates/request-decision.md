---
schema: pdca.request-decision/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
decision_id: null
scope_kind: task
work_id: null
tree_revision: null
request_id: null
request_digest: null
kind: null
phase: null
run_id: null
conversation_ref: null
subject_ref: null
subject_digest: null
terminal_state: null
response: null
response_ref: null
source_ref: null
backend_order_receipt_ref: null
---

# 确认消费记录

固定请求、原始响应来源及真实顺序，核对task/attempt/phase/run/会话/对象一致。只有consumed + confirmed且未撤权可启动该run；rejected/cancelled/superseded不授权。

工作级work_action按work/tree/action/固定对象匹配，不虚构task/phase；离线task trace检查器不涵盖工作级裁决。

这是可审计投影，不是签发器。不能凭执行Agent自填字段产生批准。相同请求重复返回原状态，不能重放；新对象要新请求，迟到消息不复活。
