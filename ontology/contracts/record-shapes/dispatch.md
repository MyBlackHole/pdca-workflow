---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 原生派发事实：记录格式

本契约只记录 agent-dispatch 的**一次原生创建事务事实**。
字段中的 null/空值表示未取得证据，不构成授权、创建成功或隔离证明。

## 示例

```markdown
---
schema: pdca.dispatch/v4
protocol_revision: 4.0.0-rc.5
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

`assignment_ref/digest` 固定本次实际提交的 assignment；
`capability_check_ref` 指向 CAP-01 的适用能力证据；
receipt、Agent/conversation identity 与 isolation/autonomy evidence 只记录真实宿主回执或可观察事实。

`status=accepted` 本身不创造 Agent，也不授权 Plan；缺失必要身份/回执时保持 unknown/blocked。
unknown 只对账同一 `dispatch_request_id`，不通过第二次创建制造新的副作用。
```
