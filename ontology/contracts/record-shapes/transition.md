---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 阶段事件，不再是固定四条自动边：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.transition-receipt/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
sequence: null
event: null
phase: null
run_id: null
previous_ref: null
previous_receipt_digest: null
actor_ref: null
conversation_ref: null
baseline_digest: null
inputs: []
confirmation_decision_refs: []
result_package_refs: []
writer_grant_ref: null
observed_control_revision: null
recorded_at: null
---

# 阶段事件，不再是固定四条自动边

event=phase_started/phase_completed/archived。开始引用该run的真实phase_start消费；完成引用实际产物与证据，之后等待。序号单任务递增，前驱链固定，重试幂等。

Check后同目标返修须新Do run及用户操作，再重新Check。未改变目标时沿用原Agent；新attempt另起完整PDCA。事件不是业务副作用的exactly-once保证，未知先对账。
```
