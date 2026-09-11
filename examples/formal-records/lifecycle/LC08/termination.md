---
schema: pdca.termination/v1
termination_id: LC08-TERM
task_id: LC08-OLD
attempt: 1
terminal_reason: user_cancelled
stop_event_ref:
  ref: stop.md
  digest: 669276a2cec73c30418ae88cb0de361f0b97f99d758e01c6c93c253f2f7dacf2
last_valid_phase: do
last_transition_ref: transition1.md
last_transition_digest: d5008ab24124d813d3354691f55c5980bffe52473fc3b20036f39b24bd6cc7a3
execution_revocation_refs:
- ref: revocation.md
  digest: 0d9302b9b6d67549c5833dabf615c908bb3ec85640a8cf9d4bd3d63a967a9a41
record_handoff_ref:
  ref: handoff.md
  digest: b3996554489589658d7ad03d29780fd5378be2a51db1ccfd00077dbc62cca7c9
inflight_operations:
- operation_id: OP1
  operation_ref:
    ref: operation.md
    digest: 67291a3ac77a1fdedc0a6e87a3c78b0ac46188a9471c158b5b4838e04d0d50bb
  status: settled
  evidence_ref:
    ref: effect-proof.md
    digest: 0641a048858804d2b9edfd4387d03ff553d933b46ba1b6a3df1cc156354167c7
settlement_refs:
- ref: effect-proof.md
  digest: 0641a048858804d2b9edfd4387d03ff553d933b46ba1b6a3df1cc156354167c7
isolation_refs: []
retained_resource_refs: []
released_resource_refs:
- ref: reservation.md
  digest: 095ce261141ee075dfea67125dc4f5740406559790c5dd38ef72b8876d24a672
sealing_owner_ref: fixture:host
backend_receipt_ref:
  ref: handoff.md
  digest: b3996554489589658d7ad03d29780fd5378be2a51db1ccfd00077dbc62cca7c9
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
