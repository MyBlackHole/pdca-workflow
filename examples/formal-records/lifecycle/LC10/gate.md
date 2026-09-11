---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: LC10-GATE
task_id: LC10-OLD
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: 557df12310f5ea09de87340d72e3336e9179854959b992bb1587e4601c17962b
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  observation_ref:
    ref: source.md
    digest: 339104d67a18b06e3dd36ea0f118cd4a4337f62e45cbdd11dd02ce48d100d879
  result: satisfied
result: ready
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
