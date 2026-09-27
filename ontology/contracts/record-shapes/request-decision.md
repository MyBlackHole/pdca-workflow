---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 用户回应匹配与消费：记录格式

本契约只记录 CONFIRM-01 中 **response 如何匹配并消费 request**。
decision 是可审计投影，不是 Gate，不写 transition，也不直接改变 task execution_state。

## 示例

```markdown
---
schema: pdca.request-decision/v4
protocol_revision: 4.0.0-rc.5
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

# 用户回应匹配与消费

固定 request、原始 response、subject/conversation/identity 匹配及可信顺序。
`terminal_state` 记录 consumed / rejected / cancelled / superseded；
只有 consumed 且 response=confirmed 才形成 **positive authorization fact**。

positive authorization 仍不等于 phase 可以开始；GATE-01 还要检查 predecessor、freshness、
control、resource/capability 等当前条件。相同 request 重复投递返回既有 decision，不再次消费。
```
