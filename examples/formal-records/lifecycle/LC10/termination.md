---
schema: pdca.termination/v1
termination_id: LC10-TERM
task_id: LC10-OLD
attempt: 1
terminal_reason: user_cancelled
stop_event_ref:
  ref: stop.md
  digest: 44471af7a674be3baa08f9432c67a0f999e9e65dd5b2f63352a8043f9cb09952
last_valid_phase: do
last_transition_ref: transition1.md
last_transition_digest: 0fa45ace5fc16edbf05b3571bcdb480c652c6e8ced437f38d5711c153ff4492f
execution_revocation_refs:
- ref: revocation.md
  digest: 6a4220b356fedf1b9c6a66b6f505737305d4ba104339a1d4cbd20e3173a35302
record_handoff_ref:
  ref: handoff.md
  digest: 78bea562ad77f13705f544b5ce30725965ee9cee73c423a0e3976e53c1d7b681
inflight_operations:
- operation_id: OP1
  operation_ref:
    ref: operation.md
    digest: 301101e0acc50b2ada7ba572b7fa5e3cc4594f2648a6dd2c569bafee9caa7aaa
  status: isolated
  evidence_ref:
    ref: effect-proof.md
    digest: 7d7b5dd71cac52921f110a5a770d45657765ffaca94e6180a6073874fa98ab98
settlement_refs: []
isolation_refs:
- ref: effect-proof.md
  digest: 7d7b5dd71cac52921f110a5a770d45657765ffaca94e6180a6073874fa98ab98
retained_resource_refs:
- ref: reservation.md
  digest: e776636dc060285f940f584465526032ea8d6ba6027f79028e45adeef3084506
released_resource_refs: []
sealing_owner_ref: fixture:host
backend_receipt_ref:
  ref: handoff.md
  digest: 78bea562ad77f13705f544b5ce30725965ee9cee73c423a0e3976e53c1d7b681
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
