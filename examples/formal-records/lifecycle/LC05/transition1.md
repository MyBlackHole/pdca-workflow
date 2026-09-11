---
schema: pdca.transition-receipt/v3.2
task_id: LC05-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: e1e48eef0b6c34b340d5287db55331275875bf70227b5fe16f3339b319f51ba7
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: e1e48eef0b6c34b340d5287db55331275875bf70227b5fe16f3339b319f51ba7
confirmation_refs:
- ref: plan_response.md
  digest: a0dbf1d901be65a03a9c20a0bfe9b04a5d53471eb26b11a42a8cf811544b5759
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
confirmation_decision_refs:
- ref: plan_decision.md
  digest: b13a49a47ab3bf001e361f98b62cb22fa28e7d2452fa59eb12d9a61c2d9d106d
writer_grant_ref:
  ref: source.md
  digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 161718205c580e7a975e2b76205646504acc11bf48aa8d34b49f7cbd55981263
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
gate_check_ref: gate.md
gate_check_digest: bbc93eeb7a770f3e36f75d51db4b5ead1be7e77e7982c5d50b9aa41805c81105
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
