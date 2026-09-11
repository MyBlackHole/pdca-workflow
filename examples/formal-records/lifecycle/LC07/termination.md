---
schema: pdca.termination/v1
termination_id: LC07-TERM
task_id: LC07-OLD
attempt: 1
terminal_reason: user_cancelled
stop_event_ref:
  ref: stop.md
  digest: ba349bbdeb1a6ba089c9a87f20d6e2580a9fd7f7774d50d5ffea24c2c47ce0fc
last_valid_phase: do
last_transition_ref: transition1.md
last_transition_digest: b7d7fa4a4e4bf66e1ca7497fec125fd3f2ce95d78898b9c0ee4bdf9b82211b49
execution_revocation_refs:
- ref: revocation.md
  digest: 1e4f2c63d4768dcfebc944f179792a4ffaa52bbd57c40ce361d2169c1f937b10
record_handoff_ref:
  ref: handoff.md
  digest: 0ea05a0e3e6cfad1935740f537e1b532f3cd807cfb588eb16d7b9aa95138535a
inflight_operations:
- operation_id: OP1
  operation_ref:
    ref: operation.md
    digest: df96aa4ef2fe45e21509d70983ea399bff2aca12494cabb72b446acf23b93e11
  status: isolated
  evidence_ref:
    ref: effect-proof.md
    digest: fc670feff3f0c0df343cbf5d42685cd022056b2567843666ad11124c7f9627e1
settlement_refs: []
isolation_refs:
- ref: effect-proof.md
  digest: fc670feff3f0c0df343cbf5d42685cd022056b2567843666ad11124c7f9627e1
retained_resource_refs:
- ref: reservation.md
  digest: 06484833a02aea31c38eb6f7bc337308ca94d8101e7a2525700f8ad99cf7dc95
released_resource_refs: []
sealing_owner_ref: fixture:host
backend_receipt_ref:
  ref: handoff.md
  digest: 0ea05a0e3e6cfad1935740f537e1b532f3cd807cfb588eb16d7b9aa95138535a
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
