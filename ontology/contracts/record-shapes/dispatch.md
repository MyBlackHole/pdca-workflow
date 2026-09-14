---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 原生派发事实：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
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
```
