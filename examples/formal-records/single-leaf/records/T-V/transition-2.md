---
schema: pdca.transition-receipt/v3.2
task_id: T-V
sequence: 2
from: do
to: check
previous_receipt_digest: 7a677b1a4724201f9cd2ec7c37fe3300f85f09a0c20b42ec99388bfe16ff11ac
baseline_digest: 003bd283ea17f0d44a811921b1874dc983829bf102a73379019a53b5574b0e48
gate_id: do_to_check
inputs:
- ref: run.md
  digest: d1f33c9c8953d73f6253b7de47121502167bd7303a8b24592cd1a41b30a983f4
confirmation_refs: []
test_run_refs:
- ref: run.md
  digest: d1f33c9c8953d73f6253b7de47121502167bd7303a8b24592cd1a41b30a983f4
result_package_refs: []
decision: approved
actor_ref: fixture:agent-V
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: e930663c6a0eddfb1e28dbf89ad22015b44738080e664fcc2895b00283e815c1
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
  digest: e930663c6a0eddfb1e28dbf89ad22015b44738080e664fcc2895b00283e815c1
gate_check_ref: gate-2.md
gate_check_digest: fc0ba70b92abad617c7494dcb5133c7615ee0a02893e6abaa7ce33bf0160fe1a
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
