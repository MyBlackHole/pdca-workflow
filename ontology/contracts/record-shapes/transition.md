---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 阶段事件 receipt：记录格式

本契约只定义 TRANSITION-01 的不可变阶段事件 receipt。
字段为空表示事实未取得；receipt 不生成授权，也不直接定义 task 当前状态。

## 示例

```markdown
---
schema: pdca.transition-receipt/v4
protocol_revision: 4.0.0-rc.5
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

# 阶段事件 receipt

`event` 只使用 `phase_started / phase_completed / archived`。

- phase_started 引用本次 GATE 实际消费的 confirmation decision 与固定输入；
- phase_completed 引用同 run 的真实 result/evidence；
- archived 引用已完成 Act 的最终处置结果。

`sequence + previous_ref/digest` 固定同 task/attempt 的事件顺序。
重复同一 run/event 不追加第二份同义事实；链分叉或前驱不明时停止。
返工、新 attempt 和业务 operation 的规则不由这个 record-shape 定义。
```
