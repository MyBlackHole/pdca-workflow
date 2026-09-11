---
schema: pdca.transition-receipt/v3.2
task_id: T-M
sequence: 2
from: do
to: check
previous_receipt_digest: 5066dd2f9fdae0fbfb8ae60672aad5e2ef4d4268d85f1571be3539f10b1b9a56
baseline_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
gate_id: do_to_check
inputs:
- ref: run.md
  digest: 005a6fab6785cf4e7f9095077868730d6205ffdcf734ce26c67a265586b9e975
confirmation_refs: []
test_run_refs:
- ref: run.md
  digest: 005a6fab6785cf4e7f9095077868730d6205ffdcf734ce26c67a265586b9e975
result_package_refs: []
decision: approved
actor_ref: fixture:agent-M
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 574eaeb008118104afecece3c87ed3579ac25b895299a6be44ce8dc0b5dba3e3
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
  ref: inputs-2.md
  digest: 574eaeb008118104afecece3c87ed3579ac25b895299a6be44ce8dc0b5dba3e3
gate_check_ref: gate-2.md
gate_check_digest: 75ebf8b7f75d3c13b0df2ad7fa52009e983f652b3d6da93f0ec1bb4b72e7af97
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
