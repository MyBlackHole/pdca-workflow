---
schema: pdca.transition-receipt/v3.2
task_id: LC06-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: 129ab28692393c75e8ea649e87abe1760caf91113a3a2d4f7850f936df750157
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: 129ab28692393c75e8ea649e87abe1760caf91113a3a2d4f7850f936df750157
confirmation_refs:
- ref: plan_response.md
  digest: 9a7cc7e11c27b361c847d6ab8a2b2903bf764f668070e00e54abeb893ff5e187
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 561c63fa28271d6ff2669f145e16acf19387cf9fa50614dc2e3496233e539655
confirmation_decision_refs:
- ref: plan_decision.md
  digest: de44f13ea795bcb8e4b7a434cc13df1e3ae309a025e5e173adc2af73ab0c34cd
writer_grant_ref:
  ref: source.md
  digest: 561c63fa28271d6ff2669f145e16acf19387cf9fa50614dc2e3496233e539655
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 771deae93d2f43e9de5dbab648f13023cde7affef2d3a6a653804caef01cdc42
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: 561c63fa28271d6ff2669f145e16acf19387cf9fa50614dc2e3496233e539655
gate_check_ref: gate.md
gate_check_digest: 230fcf5089c2b530088fd3df381216667e00b1e0a153a5429448fcd8fee86681
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
