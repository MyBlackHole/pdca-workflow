---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# Side-effect operation 事实：记录格式

本契约只保存一次真实副作用调用的事实与对账状态。
它不是执行器、资源锁、重试策略或 phase 授权。

## 示例

```markdown
---
schema: pdca.operation/v4
protocol_revision: 4.0.0-rc.5
task_id: null
attempt: null
run_id: null
operation_id: null
reservation_ref: null
resource_ref: null
arguments_digest: null
idempotency_key: null
idempotency_evidence_ref: null
status: planned
backend_request_ref: null
result_ref: null
reconciliation_ref: null
---

# Side-effect operation 事实

`planned / submitted / unknown / succeeded / failed / settled` 只描述观察到的调用状态。
登记与调用之间中断不能证明“未调用”；无可靠返回时保持 unknown，并以同一 operation_id 对账原请求。

`idempotency_key/evidence` 只记录后端真实幂等依据，不因为字段存在就允许重试。
是否可重试、是否阻止资源 released，由 RESOURCE-01 根据真实 backend/reconciliation 事实判断。

operation record 不改变 task phase/state，也不创造额外参数、资源范围或用户授权。
```
