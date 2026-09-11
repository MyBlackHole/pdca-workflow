---
schema: pdca.transition-receipt/v3.2
task_id: T-P
sequence: 2
from: do
to: check
previous_receipt_digest: b509d03203ef679f2aeef13e441a9542a5a12b73c1378d1cdd20ecefd45cad11
baseline_digest: ad325e8776955f7f9154d2de5e9f4d1e99bc6b602465f713c1aed496218a0bd0
gate_id: do_to_check
inputs:
- ref: run.md
  digest: 0a22481714bcc34ad8dce6d5337cedcad7adf1127d15e439d5199330eb68b693
confirmation_refs: []
test_run_refs:
- ref: run.md
  digest: 0a22481714bcc34ad8dce6d5337cedcad7adf1127d15e439d5199330eb68b693
result_package_refs: []
decision: approved
actor_ref: fixture:agent-P
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 4dca8cd9c6c509b4e62f8650e60e63d055ff5fcff6820012cc578a7cde5ecc84
confirmation_decision_refs: []
writer_grant_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
observed_control_revision: 1
commit_receipt_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: inputs-2.md
  digest: 4dca8cd9c6c509b4e62f8650e60e63d055ff5fcff6820012cc578a7cde5ecc84
gate_check_ref: gate-2.md
gate_check_digest: 276bbca57fd7ce9d10be71255f46ef1d082bee478f3f60e7c754810b876ee00d
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
