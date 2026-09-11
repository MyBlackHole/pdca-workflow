---
schema: pdca.transition-receipt/v3.2
task_id: T-V
sequence: 4
from: act
to: archive
previous_receipt_digest: 9dc0b30ec12f1d29096304c9fcde32369a699ebe57b16a5bb146b13c9a4a37c4
baseline_digest: 003bd283ea17f0d44a811921b1874dc983829bf102a73379019a53b5574b0e48
gate_id: act_to_archive
inputs:
- ref: delivery.md
  digest: dcccc159d5c721739ddc61edcfcefe7fc3a5bbb703667b30a1e0d5690319bb22
confirmation_refs: []
test_run_refs:
- ref: run.md
  digest: d1f33c9c8953d73f6253b7de47121502167bd7303a8b24592cd1a41b30a983f4
result_package_refs:
- ref: review.md
  digest: 18c44010e52b702b76f354f4e59e951cacebf389ef7646d1e892d4a1ce460da7
decision: approved
actor_ref: fixture:agent-V
recorded_at: null
protocol_revision: 3.4.4
attempt: 1
inputs_digest: c374f55b62eac906ee2188b8fefc1dbe660b40f9411e4dade2584d1df51ae411
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
  digest: c374f55b62eac906ee2188b8fefc1dbe660b40f9411e4dade2584d1df51ae411
gate_check_ref: gate-4.md
gate_check_digest: 133d5dcfc092603a7fcdf28a9d1a676047962943335ea2f353fc1bd40fa06c75
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
