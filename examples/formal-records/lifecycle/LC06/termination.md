---
schema: pdca.termination/v1
termination_id: LC06-TERM
task_id: LC06-OLD
attempt: 1
terminal_reason: user_cancelled
stop_event_ref:
  ref: stop.md
  digest: f7b97cae8e6029be799e16f24817d6e0a0bc005828e7bc506fc5e2107e36a4a9
last_valid_phase: do
last_transition_ref: transition1.md
last_transition_digest: 3ced836af02f7980826a5eb9d2a8712a02b1b70b7238863bd4c7206bea2bdd58
execution_revocation_refs:
- ref: revocation.md
  digest: f7c048f34e7fdc20522d59fdc9219e17bdc2e32e4b06ae07e54b2ef10b4aa7a6
record_handoff_ref:
  ref: handoff.md
  digest: d9ed19252c119b351506ff8fc363aa049997911912d9228ef533e4cdf2d8a225
inflight_operations:
- operation_id: OP1
  operation_ref:
    ref: operation.md
    digest: ed0d95113f916137e64e8d1f6002659b70fd244b33be2abd122fa16c19fac181
  status: settled
  evidence_ref:
    ref: effect-proof.md
    digest: 142db3ee86dda1c0f445a75c0f39c8cca8397dd75be6909a91761b4acba4b33e
settlement_refs:
- ref: effect-proof.md
  digest: 142db3ee86dda1c0f445a75c0f39c8cca8397dd75be6909a91761b4acba4b33e
isolation_refs: []
retained_resource_refs: []
released_resource_refs:
- ref: reservation.md
  digest: 342310ee4da2c04a8066ec8315223e4c39c7260f735cd694070c93b08727fee4
sealing_owner_ref: fixture:host
backend_receipt_ref:
  ref: handoff.md
  digest: d9ed19252c119b351506ff8fc363aa049997911912d9228ef533e4cdf2d8a225
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
