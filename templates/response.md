---
schema: pdca.response/v3.2
task_id: null
request_id: null
kind: null
subject_digest: null
response: null
source_ref: null
actor_ref: null
conversation_ref: null
recorded_at: null
protocol_revision: 3.4.10
attempt: null
phase: null
subject_ref: null
host_received_event_ref: null
---

# 独立响应

仅由TASK-01授权的可信消息通道填写；子Agent不得填写自己的批准响应。

## 来源

用户确认必须定位真实用户消息或可信宿主回执；澄清响应必须定位当前任务真实用户消息。时间未知留空，不能倒填。

## 决定和理由

用户确认响应为confirmed/rejected/needs_change；clarification响应为clarification_answer，澄清回答本身不是阶段批准。

记录真实意见、发现、局限及需要补足的材料。请求ID、task_id、对象摘要任一不符则不得消费。

此文件只保存真实回应，不等于批准已经消费。CONTROL-01决策回执匹配身份、期限和任务控制状态后才可供门禁使用；Agent不能签自己的确认。
