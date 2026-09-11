---
schema: pdca.fixture-expectations/v1
profile: fixed_formal_record_example
provenance: synthetic_maintainer_spec_not_user_authorization
work_id: W
tree_revision: TR
nodes:
- node_id: N
  parent_node_id: null
  children: []
formal_records:
  inputs/protocol.md: subject-snapshot
  inputs/subject.md: subject-snapshot
  cases/entry/ME01.md: test-case
  cases/entry/ME02.md: test-case
  cases/entry/ME03.md: test-case
  cases/entry/ME04.md: test-case
  cases/entry/ME05.md: test-case
  cases/entry/ME06.md: test-case
  cases/entry/ME07.md: test-case
  cases/entry/ME08.md: test-case
  cases/entry/ME09.md: test-case
  cases/entry/ME10.md: test-case
  cases/entry/ME11.md: test-case
  cases/entry/ME12.md: test-case
  cases/entry/ME13.md: test-case
  cases/entry/ME14.md: test-case
  suites/entry.md: test-suite
  bindings/ME01.md: test-case-binding
  bindings/ME02.md: test-case-binding
  bindings/ME03.md: test-case-binding
  bindings/ME04.md: test-case-binding
  bindings/ME05.md: test-case-binding
  bindings/ME06.md: test-case-binding
  bindings/ME07.md: test-case-binding
  bindings/ME08.md: test-case-binding
  bindings/ME09.md: test-case-binding
  bindings/ME10.md: test-case-binding
  bindings/ME11.md: test-case-binding
  bindings/ME12.md: test-case-binding
  bindings/ME13.md: test-case-binding
  bindings/ME14.md: test-case-binding
  cases/modeling/MODELING-P.md: test-case
  cases/modeling/MODELING-N.md: test-case
  suites/node-modeling.md: test-suite
  cases/projection/PROJECTION-P.md: test-case
  cases/projection/PROJECTION-N.md: test-case
  suites/node-projection.md: test-suite
  cases/verification/VERIFICATION-P.md: test-case
  cases/verification/VERIFICATION-N.md: test-case
  suites/node-verification.md: test-suite
  artifacts/node.md: work-node
  graph.md: dependency-snapshot
  graph-check.md: dependency-check
  records/T-M/baseline.md: baseline
  records/T-M/run.md: test-run
  records/T-M/review.md: review-package
  records/T-M/plan-request.md: request
  records/T-M/plan-response.md: response
  records/T-M/plan-decision.md: request-decision
  records/T-M/check-request.md: request
  records/T-M/check-response.md: response
  records/T-M/check-decision.md: request-decision
  records/T-M/delivery.md: delivery
  records/T-M/gate-1.md: gate-check
  records/T-M/transition-1.md: transition
  records/T-M/gate-2.md: gate-check
  records/T-M/transition-2.md: transition
  records/T-M/gate-3.md: gate-check
  records/T-M/transition-3.md: transition
  records/T-M/gate-4.md: gate-check
  records/T-M/transition-4.md: transition
  records/T-M/archive.md: archive-receipt
  records/T-M/task.md: task
  records/T-P/baseline.md: baseline
  records/T-P/run.md: test-run
  records/T-P/review.md: review-package
  records/T-P/plan-request.md: request
  records/T-P/plan-response.md: response
  records/T-P/plan-decision.md: request-decision
  records/T-P/check-request.md: request
  records/T-P/check-response.md: response
  records/T-P/check-decision.md: request-decision
  records/T-P/delivery.md: delivery
  records/T-P/gate-1.md: gate-check
  records/T-P/transition-1.md: transition
  records/T-P/gate-2.md: gate-check
  records/T-P/transition-2.md: transition
  records/T-P/gate-3.md: gate-check
  records/T-P/transition-3.md: transition
  records/T-P/gate-4.md: gate-check
  records/T-P/transition-4.md: transition
  records/T-P/archive.md: archive-receipt
  records/T-P/task.md: task
  records/T-V/baseline.md: baseline
  records/T-V/run.md: test-run
  records/T-V/review.md: review-package
  records/T-V/plan-request.md: request
  records/T-V/plan-response.md: response
  records/T-V/plan-decision.md: request-decision
  records/T-V/check-request.md: request
  records/T-V/check-response.md: response
  records/T-V/check-decision.md: request-decision
  records/T-V/delivery.md: delivery
  records/T-V/gate-1.md: gate-check
  records/T-V/transition-1.md: transition
  records/T-V/gate-2.md: gate-check
  records/T-V/transition-2.md: transition
  records/T-V/gate-3.md: gate-check
  records/T-V/transition-3.md: transition
  records/T-V/gate-4.md: gate-check
  records/T-V/transition-4.md: transition
  records/T-V/archive.md: archive-receipt
  records/T-V/task.md: task
  tree-spec.md: tree-spec
  tree-manifest.md: tree-manifest
suites:
  suites/entry.md:
    suite_id: SUITE-ENTRY
    node_id: N
    scene: ontology_modeling
    required_cases:
    - ME01
    - ME02
    - ME03
    - ME04
    - ME05
    - ME06
    - ME07
    - ME08
    - ME09
    - ME10
    - ME11
    - ME12
    - ME13
    - ME14
  suites/node-modeling.md:
    suite_id: SUITE-MODELING
    node_id: N
    scene: ontology_modeling
    required_cases:
    - MODELING-P
    - MODELING-N
  suites/node-projection.md:
    suite_id: SUITE-PROJECTION
    node_id: N
    scene: ontology_projection
    required_cases:
    - PROJECTION-P
    - PROJECTION-N
  suites/node-verification.md:
    suite_id: SUITE-VERIFICATION
    node_id: N
    scene: ontology_conformance_verification
    required_cases:
    - VERIFICATION-P
    - VERIFICATION-N
entry_parameters:
- original_request_or_parent_seed
- protocol_snapshot
- authorized_scope
- requirement_mapping
- current_task_identity
- real_tool_binding
- work_budget
graph_path: graph.md
graph_check_path: graph-check.md
required_events:
- freeze
- release
required_edges:
- - ontology_modeling
  - freeze
- - freeze
  - ontology_projection
- - ontology_projection
  - release
- - release
  - ontology_conformance_verification
manifest_path: tree-manifest.md
required_roles:
- tree_spec
- node
- suite
- modeling_delivery
- modeling_terminal
- protocol_baseline
- subject_snapshot
- graph
- graph_check
gate_predicates:
  plan_to_do:
  - identity_and_input
  - graph
  - fixed_baseline_tests_budget
  - capability
  - resource
  - confirmation
  - control
  do_to_check:
  - case_observations
  - fixed_artifacts
  - side_effects
  - record_control
  - integrity
  check_to_act:
  - ac_verdict_issues
  - subject_conformance_if_review
  - confirmation
  - control
  act_to_archive:
  - knowledge_and_rework
  - honest_delivery
  - no_pending_requests
  - side_effects_settled
  - recoverable_chain
  - control
task_groups:
- task: records/T-M/task.md
  baseline: records/T-M/baseline.md
  baseline_digest: 3358a67a8e390fbfc3670af90614b20a486ec4f510bac3cc77ba97c1eb65f2b6
  review: records/T-M/review.md
  run: records/T-M/run.md
  delivery: records/T-M/delivery.md
  archive: records/T-M/archive.md
  artifact: artifacts/node.md
  transitions:
  - records/T-M/transition-1.md
  - records/T-M/transition-2.md
  - records/T-M/transition-3.md
  - records/T-M/transition-4.md
  identity:
    task_id: T-M
    work_id: W
    tree_revision: TR
    node_id: N
    scene: ontology_modeling
    attempt: 1
  plan_request: records/T-M/plan-request.md
  plan_response: records/T-M/plan-response.md
  plan_decision: records/T-M/plan-decision.md
  check_request: records/T-M/check-request.md
  check_response: records/T-M/check-response.md
  check_decision: records/T-M/check-decision.md
- task: records/T-P/task.md
  baseline: records/T-P/baseline.md
  baseline_digest: ad325e8776955f7f9154d2de5e9f4d1e99bc6b602465f713c1aed496218a0bd0
  review: records/T-P/review.md
  run: records/T-P/run.md
  delivery: records/T-P/delivery.md
  archive: records/T-P/archive.md
  artifact: artifacts/projection.md
  transitions:
  - records/T-P/transition-1.md
  - records/T-P/transition-2.md
  - records/T-P/transition-3.md
  - records/T-P/transition-4.md
  identity:
    task_id: T-P
    work_id: W
    tree_revision: TR
    node_id: N
    scene: ontology_projection
    attempt: 1
  plan_request: records/T-P/plan-request.md
  plan_response: records/T-P/plan-response.md
  plan_decision: records/T-P/plan-decision.md
  check_request: records/T-P/check-request.md
  check_response: records/T-P/check-response.md
  check_decision: records/T-P/check-decision.md
- task: records/T-V/task.md
  baseline: records/T-V/baseline.md
  baseline_digest: 003bd283ea17f0d44a811921b1874dc983829bf102a73379019a53b5574b0e48
  review: records/T-V/review.md
  run: records/T-V/run.md
  delivery: records/T-V/delivery.md
  archive: records/T-V/archive.md
  artifact: artifacts/verification.md
  transitions:
  - records/T-V/transition-1.md
  - records/T-V/transition-2.md
  - records/T-V/transition-3.md
  - records/T-V/transition-4.md
  identity:
    task_id: T-V
    work_id: W
    tree_revision: TR
    node_id: N
    scene: ontology_conformance_verification
    attempt: 1
  plan_request: records/T-V/plan-request.md
  plan_response: records/T-V/plan-response.md
  plan_decision: records/T-V/plan-decision.md
  check_request: records/T-V/check-request.md
  check_response: records/T-V/check-response.md
  check_decision: records/T-V/check-decision.md
root_node_id: N
tree_spec_path: tree-spec.md
---

固定、独立传入的合成验收依据；不是从待测候选的required字段推导，也不是用户批准。基础fixture/反例在同一basis下检查；修改basis须显式给出新摘要。
