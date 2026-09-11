---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: GC-M1
task_id: T-M
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  evidence_refs:
  - ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  verification_action: fixture predicate observation only
  observation_ref:
    ref: ../../inputs/host-source.md
    digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
  result: satisfied
result: ready
limitations:
- simulated gate, not authentic host approval
requirements_basis_ref: null
requirements_basis_digest: null
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
