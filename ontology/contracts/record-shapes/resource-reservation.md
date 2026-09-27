---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# 资源 reservation 事实：记录格式

本契约只保存 RESOURCE-01 的真实 ownership / reservation 事实。
字段为空表示事实未取得；写入状态值不会产生后端锁、授权或 task state。

## 示例

```markdown
---
schema: pdca.resource-reservation/v4
protocol_revision: 4.0.0-rc.4
reservation_id: null
owner_task_id: null
owner_attempt: null
run_id: null
ledger_writer_ref: null
authorization_ref: null
state: requested
guarantee_profile: null
resource_set: []
canonicalization_evidence_refs: []
backend_acquire_ref: null
ownership_epoch: null
operation_refs: []
revocation_ref: null
settlement_ref: null
retained_scope: null
release_conditions: []
---

# 资源 reservation 事实

`resource_set` 保存真实 canonical resource identity、scope/access 与规范化证据。
`requested / held / revoking / released / retained` 只记录 RESOURCE-01 已核实的生命周期事实。

- held 需要真实 backend acquire/ownership 依据；
- revoking 引用控制/撤销依据，但不等于已释放；
- released 需要 settlement 证明 owner 与在途 operation 已结清；
- retained 保存未决影响、隔离范围和 release conditions。

reservation state 不直接授权 phase，也不直接修改 task execution_state；GATE/STATE 只消费这些事实。
```
