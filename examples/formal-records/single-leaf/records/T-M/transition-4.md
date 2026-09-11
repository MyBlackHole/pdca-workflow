---
schema: pdca.transition-receipt/v3.2
task_id: T-M
sequence: 4
from: act
to: archive
previous_receipt_digest: 12464810aeaa5875701008e9b798bccdacecfee5c63adf1c869f9faa031a4914
baseline_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
gate_id: act_to_archive
inputs:
- ref: delivery.md
  digest: 4016dc778178c6d9c94166472aaba953e4bbae9d701d7622c3cecc6bc69d9b69
confirmation_refs: []
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
inputs_digest: 67cc86b672638fcd3060f9fb359a98e086b72340c1fe5ed4cffb3f457cc462b2
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
  digest: 67cc86b672638fcd3060f9fb359a98e086b72340c1fe5ed4cffb3f457cc462b2
gate_check_ref: gate-4.md
gate_check_digest: 631399a3a61b592bfe368eb84f87654c162170798043497e15a597b455d9f67b
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
