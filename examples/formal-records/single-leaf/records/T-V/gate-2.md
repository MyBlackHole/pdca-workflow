---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: GC-V2
task_id: T-V
attempt: 1
gate_id: do_to_check
subject_ref: run.md
subject_digest: d1f33c9c8953d73f6253b7de47121502167bd7303a8b24592cd1a41b30a983f4
observed_control_revision: 1
checks:
- predicate_id: case_observations
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
- predicate_id: fixed_artifacts
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
- predicate_id: side_effects
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
- predicate_id: record_control
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
- predicate_id: integrity
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
