---
schema: pdca.request/v3.2
task_id: null
request_id: null
kind: null
phase: null
subject_ref: null
subject_digest: null
producer_ref: null
conversation_ref: null
created_at: null
protocol_revision: 3.4.10
attempt: null
wait_policy_ref: null
wait_policy_digest: null
deadline: null
time_source_ref: null
---

# 当前任务请求

kind为plan_confirmation/check_confirmation/clarification之一。匹配当前阶段，采用真实对象摘要，不能写假身份。

## 请求事项

明确需要确认或澄清的具体对象、目标和风险。

## 固定输入

列出基线、证据、产物的版本和摘要；提交后不更改同一请求的对象。发生变化建立新请求并保留旧记录。

## 暂停与返回

请求未获匹配的真实响应前保持相应等待状态；完成事件不能越过未满足请求。

## 期限和终局

按CONTROL-01具体化deadline；explicit_wait无自动截止。可信请求决策而非Agent消息时间决定consumed/expired/cancelled/superseded；相同request_id不换对象，迟到响应不能复活。
