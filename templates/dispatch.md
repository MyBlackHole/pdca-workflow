---
schema: pdca.dispatch/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
dispatch_request_id: null
status: pending
agent_id: null
conversation_ref: null
assignment_ref: null
assignment_digest: null
spawn_receipt_ref: null
isolation_evidence_ref: null
autonomy_evidence_ref: null
capability_check_ref: null
handoff_completed: false
---

# 原生派发事实

填写实际调用／参数／原始返回与原生身份。pending/accepted/unknown/blocked/error分别说明；未知只对账原request。false表示尚未证实，不是默认失败产品。

新上下文、可交互、原会话继续分别引用证据。字段写accepted不创造Agent；工具结果看不到独立原生身份或状态时保留unknown。派发成功不授权Plan。
