---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: LC09-GATE
task_id: LC09-OLD
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: 717a850bea6859e7483678806976c3f4a19b28112ce5755384792f02e4d6b7ac
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  observation_ref:
    ref: source.md
    digest: f81eab524049bea5e7180616e9ee1b8808e3df6f99da6f4609dcbbdc603a41bd
  result: satisfied
result: ready
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
