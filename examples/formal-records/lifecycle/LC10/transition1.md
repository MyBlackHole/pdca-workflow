---
schema: pdca.transition-receipt/v3.2
task_id: LC10-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: 557df12310f5ea09de87340d72e3336e9179854959b992bb1587e4601c17962b
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: 557df12310f5ea09de87340d72e3336e9179854959b992bb1587e4601c17962b
confirmation_refs:
- ref: plan_response.md
  digest: 7d16d8ae665e193756f0d2b30d5131357206263eec577f8c1a5911e4660eb4bf
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
confirmation_decision_refs:
- ref: plan_decision.md
  digest: 2b43658dfbe40d22b6ff0daf852cb064efb31afa37a6d7f221a4b519b49e308a
writer_grant_ref:
  ref: source.md
  digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 9bc441810fb7743f4b5dbda0b4daa247ea42752bc2ad989bceb8166e4f54278f
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
gate_check_ref: gate.md
gate_check_digest: 61d4779441300bec1a0d76f8ea8d2c29eadb32ec981363993366ff3de9d86998
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
