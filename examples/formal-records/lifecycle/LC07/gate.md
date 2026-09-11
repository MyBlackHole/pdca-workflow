---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: LC07-GATE
task_id: LC07-OLD
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: e1e6242ad58b4c0513317f7aa47bb5bbc8658d3327f07f69af1266414798b996
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  observation_ref:
    ref: source.md
    digest: c8df69cbf549bd065103f65d5a5ffbada3f11cf63a5f15cb430b0b064c59eba6
  result: satisfied
result: ready
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
