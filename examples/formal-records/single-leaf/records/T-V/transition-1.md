---
schema: pdca.transition-receipt/v3.2
task_id: T-V
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: 003bd283ea17f0d44a811921b1874dc983829bf102a73379019a53b5574b0e48
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: 003bd283ea17f0d44a811921b1874dc983829bf102a73379019a53b5574b0e48
confirmation_refs:
- ref: plan-response.md
  digest: db2f73c2706df0cc4d4ef4c55408e069363ce3e67a776a79f6d439eee173b2c9
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:agent-V
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 6aa13491dfbb320e240dbf0ddeef7795a7ad43e41ce5acfd967d8a2ba73b9d8d
confirmation_decision_refs:
- ref: plan-decision.md
  digest: c609d3fbb298e42a3eb79f07bceb3352a0dd42be5fa6601e47ff8c878574644e
writer_grant_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
observed_control_revision: 1
commit_receipt_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: inputs-1.md
  digest: 6aa13491dfbb320e240dbf0ddeef7795a7ad43e41ce5acfd967d8a2ba73b9d8d
gate_check_ref: gate-1.md
gate_check_digest: 83843ec3f2da68fbeccdf95ada5950a2d34b34eb7d7be5a0159b9f05a646c103
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
