---
schema: pdca.transition-receipt/v3.2
task_id: T-M
sequence: 3
from: check
to: act
previous_receipt_digest: f0bcc1d6ae40c5061fab29a4fb3f3368b69a5b65af80f0e20c4880bbbad6f927
baseline_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
gate_id: check_to_act
inputs:
- ref: review.md
  digest: 3135251561a449216af0aeb4780548c73648eb259913df7512fe83395f4b7462
confirmation_refs:
- ref: check-response.md
  digest: 1e77b651bbbe4f83061b11035389664dc0de74f7c230f1b42b3ead67485e3e59
test_run_refs:
- ref: run.md
  digest: 005a6fab6785cf4e7f9095077868730d6205ffdcf734ce26c67a265586b9e975
result_package_refs:
- ref: review.md
  digest: 3135251561a449216af0aeb4780548c73648eb259913df7512fe83395f4b7462
decision: approved
actor_ref: fixture:agent-M
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: c132e11ec8178e8e2833ccdb60fb2466d6f4d6ea808ae6615e5bca8f155fbf70
confirmation_decision_refs:
- ref: check-decision.md
  digest: 6a20011b42d0aa598c9b39426d288b330a27b4a76aba85672c392f2e99b391e9
writer_grant_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
observed_control_revision: 1
commit_receipt_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: inputs-3.md
  digest: c132e11ec8178e8e2833ccdb60fb2466d6f4d6ea808ae6615e5bca8f155fbf70
gate_check_ref: gate-3.md
gate_check_digest: 7b633fc516740ca5da566df3901a5836e617aeaee394b30245888c41c0a4f780
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
