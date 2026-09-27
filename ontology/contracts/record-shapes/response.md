---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# 用户真实回应：记录格式

本契约只保存 CONFIRM-01 使用的**原始用户回应事实**。
它不判断回应是否匹配 request，也不产生授权结果。

## 示例

```markdown
---
schema: pdca.response/v4
protocol_revision: 4.0.0-rc.4
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

# 用户真实回应

保存原始文字、可核实消息/transcript 来源、actor、conversation/routing 与宿主接收事实。
`response` 记录用户表达（如 confirmed/rejected/needs_change/clarification_answer），
但是否能消费为当前 request 的授权由 request-decision 另行匹配。

Agent 抄录、父 Agent 转述、标签或哈希不能替代真实用户来源；来源无法核实时保持 unknown/等待。
```
