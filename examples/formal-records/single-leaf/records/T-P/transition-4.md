---
schema: pdca.transition-receipt/v3.2
task_id: T-P
sequence: 4
from: act
to: archive
previous_receipt_digest: 3fc3a257d1d7a65dbc85ed7f33dc6c080d41db59a082b3dc5afeef0a0fde4029
baseline_digest: ad325e8776955f7f9154d2de5e9f4d1e99bc6b602465f713c1aed496218a0bd0
gate_id: act_to_archive
inputs:
- ref: delivery.md
  digest: 7c29f93ba4c31938dcace41949c7da5deab67f50f14a7c179956ef95016313ce
confirmation_refs: []
test_run_refs:
- ref: run.md
  digest: 0a22481714bcc34ad8dce6d5337cedcad7adf1127d15e439d5199330eb68b693
result_package_refs:
- ref: review.md
  digest: 0e94a1670f7e8aca03ccfc77b83fcf1578512121ba1adce403dbd86c81dca905
decision: approved
actor_ref: fixture:agent-P
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 92744ff8540a0e739f66040fe3148b0656865aef7b21815fd220a48541ca79f6
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
  ref: inputs-4.md
  digest: 92744ff8540a0e739f66040fe3148b0656865aef7b21815fd220a48541ca79f6
gate_check_ref: gate-4.md
gate_check_digest: ca2365888358b63f3604fa62f7fa4696bcd0d96db413c300d3dc8722eb1e9ace
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
