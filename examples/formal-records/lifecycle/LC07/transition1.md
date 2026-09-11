---
schema: pdca.transition-receipt/v3.2
task_id: LC07-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: e1e6242ad58b4c0513317f7aa47bb5bbc8658d3327f07f69af1266414798b996
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: e1e6242ad58b4c0513317f7aa47bb5bbc8658d3327f07f69af1266414798b996
confirmation_refs:
- ref: plan_response.md
  digest: d305d650e35d7f172284d62e172a08279376cbf83b36e8c84889e0cf407d57d4
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
confirmation_decision_refs:
- ref: plan_decision.md
  digest: 7b3d0a0a47621c39fff629da3bf9010e947bae9eb650d43d2d272873ffb42dd5
writer_grant_ref:
  ref: source.md
  digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 6134587b0e4d6422e1ed44f360ebc920d0c0a1964ff280a5c5d155a9df100d75
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
gate_check_ref: gate.md
gate_check_digest: 3504df9e882f6b551a1629a89f467611091da63470fd255e3eb2d61cc5955db1
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
