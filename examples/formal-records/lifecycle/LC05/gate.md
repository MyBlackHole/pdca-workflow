---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: LC05-GATE
task_id: LC05-OLD
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: e1e48eef0b6c34b340d5287db55331275875bf70227b5fe16f3339b319f51ba7
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  observation_ref:
    ref: source.md
    digest: ccb3b7f42521972acdfe2bc4452b7f7056736f45db44b92d4d398d5968ffbde0
  result: satisfied
result: ready
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
