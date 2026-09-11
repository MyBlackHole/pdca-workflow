---
schema: pdca.gate-check/v1
protocol_revision: 3.4.4
check_id: LC08-GATE
task_id: LC08-OLD
attempt: 1
gate_id: plan_to_do
subject_ref: baseline.md
subject_digest: bc0db796124d10145875ae2cf74274815612fee2d27828cf6d407b1fd3e206fc
observed_control_revision: 1
checks:
- predicate_id: identity_and_input
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: graph
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: fixed_baseline_tests_budget
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: capability
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: resource
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: confirmation
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
- predicate_id: control
  required: true
  authority_ref: GATE-01
  verification_action: 核对具名fixture关系
  evidence_refs:
  - ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  observation_ref:
    ref: source.md
    digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
  result: satisfied
result: ready
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
