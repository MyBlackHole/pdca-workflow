---
schema: pdca.transition-receipt/v3.2
task_id: T-P
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: ad325e8776955f7f9154d2de5e9f4d1e99bc6b602465f713c1aed496218a0bd0
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: ad325e8776955f7f9154d2de5e9f4d1e99bc6b602465f713c1aed496218a0bd0
confirmation_refs:
- ref: plan-response.md
  digest: c28162cc2fa5d781024b7473a346d597d23c34190ba2588b5bb7c8a51dbe9b05
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:agent-P
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 223ad4ec9c5c2cd6a956d6a34a86863b43a1ddbe9a37798171aa381a8c244d17
confirmation_decision_refs:
- ref: plan-decision.md
  digest: 1d661b1f86999c476d30ecc555309eaf95b2594d8209d242409490105a30724f
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
  digest: 223ad4ec9c5c2cd6a956d6a34a86863b43a1ddbe9a37798171aa381a8c244d17
gate_check_ref: gate-1.md
gate_check_digest: e29ec85cdd4b7a54cfb31529ed9bf27282acc6507677017377bf448da290fc32
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
