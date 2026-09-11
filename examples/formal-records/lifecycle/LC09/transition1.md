---
schema: pdca.transition-receipt/v3.2
task_id: LC09-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: 717a850bea6859e7483678806976c3f4a19b28112ce5755384792f02e4d6b7ac
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: 717a850bea6859e7483678806976c3f4a19b28112ce5755384792f02e4d6b7ac
confirmation_refs:
- ref: plan_response.md
  digest: 036fd039f07640f95f517dfa3e02a5b66df5778aed6cc38af4a2cc2d7ee8936f
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
confirmation_decision_refs:
- ref: plan_decision.md
  digest: 07f673f5e340789edffa4e2f46c865af9fb5397d1d1931a5dfe1bba2ebdb736f
writer_grant_ref:
  ref: source.md
  digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 64191228ffe2ab745d615f23b0c2e4faee6b43acdf7936da1240e387ea76c0bf
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
gate_check_ref: gate.md
gate_check_digest: 7411b5e25897c78176326eb5ca639ef41cddeb87c6535bfffc91be614df201ba
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
