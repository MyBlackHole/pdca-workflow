---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 用户待决对象：记录格式

本契约只定义 CONFIRM-01 中 **request 如何固定一个待用户决定的对象**。
null/空值表示事实未取得；request 本身不产生授权，也不表示 Gate ready。

## 示例

```markdown
---
schema: pdca.request/v4
protocol_revision: 4.0.0-rc.3
task_id: null
attempt: null
request_id: null
scope_kind: task
work_id: null
tree_revision: null
action: null
kind: phase_start
phase: null
run_id: null
subject_ref: null
subject_digest: null
conversation_ref: null
producer_ref: null
input_refs: []
created_at: null
---

# 用户待决对象

`kind=phase_start` 时固定 task/attempt/phase/run/subject；
`kind=work_action` 时固定 work/tree/action/subject，task/attempt/phase/run 保持不适用的空值；
`kind=clarification` 只固定待补事实。

`subject_ref/digest` 指向不可变的当前待决对象，而不是会继续变化的 task.md。
对象变化后创建新 request；不要原位改写旧 request 来迁移授权。
```
