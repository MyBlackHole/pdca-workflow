---
schema: pdca.transition-receipt/v3.2
task_id: T-M
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
confirmation_refs:
- ref: plan-response.md
  digest: dace32efe6278597ff9f1e9af20ce60e4d01d50a86f01655de9e3e291f147931
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:agent-M
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: bb7cd1e145b2c0bfc1f80136cefbaf20d5c895699d6673cab340faa938d870d6
confirmation_decision_refs:
- ref: plan-decision.md
  digest: ae6e0637e274648561958bb357eae4ed358a7837ddb1c46a492a6b163362b23d
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
  digest: bb7cd1e145b2c0bfc1f80136cefbaf20d5c895699d6673cab340faa938d870d6
gate_check_ref: gate-1.md
gate_check_digest: af1f98bd77705e15d51bfab9c9964400a31481c55db9a2e44aa06676f510506e
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
