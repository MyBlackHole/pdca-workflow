---
schema: pdca.termination/v1
termination_id: LC09-TERM
task_id: LC09-OLD
attempt: 1
terminal_reason: user_cancelled
stop_event_ref:
  ref: stop.md
  digest: 9c0c634c43248f642c601d22cca7eaf0e84d80277da625fa6e91e4747b35c45e
last_valid_phase: do
last_transition_ref: transition1.md
last_transition_digest: 3aa90bb8e16dc60a8dff6cfc79bcc719fe2698113469a1047f381b0689ffee26
execution_revocation_refs:
- ref: revocation.md
  digest: 3c7d3299c7bcbe8431e3cb495c6e1d69f558129bd96b95d6a6a916ded7d1ee57
record_handoff_ref:
  ref: handoff.md
  digest: 2c8569e67c3bf1a4e663fc9889bb4db72c460eb8a87ca00c46c76df01857cb34
inflight_operations:
- operation_id: OP1
  operation_ref:
    ref: operation.md
    digest: 323c5379773628b5ac183e4d40dc4454e4da044baf6a651fa1aaa1effa22023d
  status: isolated
  evidence_ref:
    ref: effect-proof.md
    digest: 72d5c9624e0f7d911109ad0dc66e945a7f252ddeeacb2949ef453febd6c4a719
settlement_refs: []
isolation_refs:
- ref: effect-proof.md
  digest: 72d5c9624e0f7d911109ad0dc66e945a7f252ddeeacb2949ef453febd6c4a719
retained_resource_refs:
- ref: reservation.md
  digest: 04542b195008011007730c7a2915c9f011f23ac9258ebd9f591970b3153cdfcd
released_resource_refs: []
sealing_owner_ref: fixture:host
backend_receipt_ref:
  ref: handoff.md
  digest: 2c8569e67c3bf1a4e663fc9889bb4db72c460eb8a87ca00c46c76df01857cb34
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
