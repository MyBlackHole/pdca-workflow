---
schema: pdca.lifecycle-example-basis/v1
profile: lifecycle_record_examples
provenance: synthetic maintainer requirements; not user authorization
protocol_revision: 3.4.4
groups:
- case_id: LC01
  identity:
    task_id: LC01-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: blocked_unexecuted
  expected_phase: plan
  records:
    source:
      path: LC01/source.md
      kind: fixture-evidence
    capability-proof:
      path: LC01/capability-proof.md
      kind: fixture-evidence
    capability:
      path: LC01/capability.md
      kind: capability-check
    control:
      path: LC01/control.md
      kind: control-state
    task:
      path: LC01/task.md
      kind: task
  transition_roles: []
  operation_roles: []
  required_operation_ids: []
  reservation_roles: []
  required_resource_ids: []
  required_capabilities:
  - independent_agent
- case_id: LC02
  identity:
    task_id: LC02-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: blocked
  expected_phase: plan
  records:
    source:
      path: LC02/source.md
      kind: fixture-evidence
    baseline:
      path: LC02/baseline.md
      kind: baseline
    capability-proof:
      path: LC02/capability-proof.md
      kind: fixture-evidence
    capability:
      path: LC02/capability.md
      kind: capability-check
    control:
      path: LC02/control.md
      kind: control-state
    task:
      path: LC02/task.md
      kind: task
  transition_roles: []
  operation_roles: []
  required_operation_ids: []
  reservation_roles: []
  required_resource_ids: []
  required_capabilities:
  - confirmation_channel
- case_id: LC03
  identity:
    task_id: LC03-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: awaiting_confirmation
  expected_phase: plan
  records:
    source:
      path: LC03/source.md
      kind: fixture-evidence
    baseline:
      path: LC03/baseline.md
      kind: baseline
    request:
      path: LC03/request.md
      kind: request
    control:
      path: LC03/control.md
      kind: control-state
    task:
      path: LC03/task.md
      kind: task
  transition_roles: []
  operation_roles: []
  required_operation_ids: []
  reservation_roles: []
  required_resource_ids: []
  request_policy: pending
- case_id: LC04
  identity:
    task_id: LC04-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: blocked
  expected_phase: plan
  records:
    source:
      path: LC04/source.md
      kind: fixture-evidence
    baseline:
      path: LC04/baseline.md
      kind: baseline
    request:
      path: LC04/request.md
      kind: request
    message:
      path: LC04/message.md
      kind: fixture-evidence
    response:
      path: LC04/response.md
      kind: response
    decision:
      path: LC04/decision.md
      kind: request-decision
    control:
      path: LC04/control.md
      kind: control-state
    task:
      path: LC04/task.md
      kind: task
  transition_roles: []
  operation_roles: []
  required_operation_ids: []
  reservation_roles: []
  required_resource_ids: []
  request_policy: rejected
- case_id: LC05
  identity:
    task_id: LC05-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: stopping
  expected_phase: do
  records:
    source:
      path: LC05/source.md
      kind: fixture-evidence
    baseline:
      path: LC05/baseline.md
      kind: baseline
    plan_request:
      path: LC05/plan_request.md
      kind: request
    plan_message:
      path: LC05/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC05/plan_response.md
      kind: response
    plan_decision:
      path: LC05/plan_decision.md
      kind: request-decision
    commit:
      path: LC05/commit.md
      kind: fixture-evidence
    gate:
      path: LC05/gate.md
      kind: gate-check
    transition1:
      path: LC05/transition1.md
      kind: transition
    stop-source:
      path: LC05/stop-source.md
      kind: fixture-evidence
    order:
      path: LC05/order.md
      kind: fixture-evidence
    stop:
      path: LC05/stop.md
      kind: control-event
    operation:
      path: LC05/operation.md
      kind: operation
    reservation:
      path: LC05/reservation.md
      kind: resource-reservation
    control:
      path: LC05/control.md
      kind: control-state
    task:
      path: LC05/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
- case_id: LC06
  identity:
    task_id: LC06-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: interrupted
  expected_phase: do
  records:
    source:
      path: LC06/source.md
      kind: fixture-evidence
    baseline:
      path: LC06/baseline.md
      kind: baseline
    plan_request:
      path: LC06/plan_request.md
      kind: request
    plan_message:
      path: LC06/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC06/plan_response.md
      kind: response
    plan_decision:
      path: LC06/plan_decision.md
      kind: request-decision
    commit:
      path: LC06/commit.md
      kind: fixture-evidence
    gate:
      path: LC06/gate.md
      kind: gate-check
    transition1:
      path: LC06/transition1.md
      kind: transition
    stop-source:
      path: LC06/stop-source.md
      kind: fixture-evidence
    order:
      path: LC06/order.md
      kind: fixture-evidence
    stop:
      path: LC06/stop.md
      kind: control-event
    operation:
      path: LC06/operation.md
      kind: operation
    revocation:
      path: LC06/revocation.md
      kind: fixture-evidence
    handoff:
      path: LC06/handoff.md
      kind: fixture-evidence
    effect-proof:
      path: LC06/effect-proof.md
      kind: fixture-evidence
    release:
      path: LC06/release.md
      kind: fixture-evidence
    reservation:
      path: LC06/reservation.md
      kind: resource-reservation
    termination:
      path: LC06/termination.md
      kind: termination
    control:
      path: LC06/control.md
      kind: control-state
    task:
      path: LC06/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
- case_id: LC07
  identity:
    task_id: LC07-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: interrupted
  expected_phase: do
  records:
    source:
      path: LC07/source.md
      kind: fixture-evidence
    baseline:
      path: LC07/baseline.md
      kind: baseline
    plan_request:
      path: LC07/plan_request.md
      kind: request
    plan_message:
      path: LC07/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC07/plan_response.md
      kind: response
    plan_decision:
      path: LC07/plan_decision.md
      kind: request-decision
    commit:
      path: LC07/commit.md
      kind: fixture-evidence
    gate:
      path: LC07/gate.md
      kind: gate-check
    transition1:
      path: LC07/transition1.md
      kind: transition
    stop-source:
      path: LC07/stop-source.md
      kind: fixture-evidence
    order:
      path: LC07/order.md
      kind: fixture-evidence
    stop:
      path: LC07/stop.md
      kind: control-event
    operation:
      path: LC07/operation.md
      kind: operation
    revocation:
      path: LC07/revocation.md
      kind: fixture-evidence
    handoff:
      path: LC07/handoff.md
      kind: fixture-evidence
    effect-proof:
      path: LC07/effect-proof.md
      kind: fixture-evidence
    reservation:
      path: LC07/reservation.md
      kind: resource-reservation
    termination:
      path: LC07/termination.md
      kind: termination
    control:
      path: LC07/control.md
      kind: control-state
    task:
      path: LC07/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
- case_id: LC08
  identity:
    task_id: LC08-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: interrupted
  expected_phase: do
  records:
    source:
      path: LC08/source.md
      kind: fixture-evidence
    baseline:
      path: LC08/baseline.md
      kind: baseline
    plan_request:
      path: LC08/plan_request.md
      kind: request
    plan_message:
      path: LC08/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC08/plan_response.md
      kind: response
    plan_decision:
      path: LC08/plan_decision.md
      kind: request-decision
    commit:
      path: LC08/commit.md
      kind: fixture-evidence
    gate:
      path: LC08/gate.md
      kind: gate-check
    transition1:
      path: LC08/transition1.md
      kind: transition
    stop-source:
      path: LC08/stop-source.md
      kind: fixture-evidence
    order:
      path: LC08/order.md
      kind: fixture-evidence
    stop:
      path: LC08/stop.md
      kind: control-event
    operation:
      path: LC08/operation.md
      kind: operation
    revocation:
      path: LC08/revocation.md
      kind: fixture-evidence
    handoff:
      path: LC08/handoff.md
      kind: fixture-evidence
    effect-proof:
      path: LC08/effect-proof.md
      kind: fixture-evidence
    release:
      path: LC08/release.md
      kind: fixture-evidence
    reservation:
      path: LC08/reservation.md
      kind: resource-reservation
    termination:
      path: LC08/termination.md
      kind: termination
    old-artifact:
      path: LC08/old-artifact.md
      kind: fixture-evidence
    successor_task:
      path: LC08/successor_task.md
      kind: task
    successor_control:
      path: LC08/successor_control.md
      kind: control-state
    successor-auth:
      path: LC08/successor-auth.md
      kind: fixture-evidence
    spawn:
      path: LC08/spawn.md
      kind: fixture-evidence
    isolation:
      path: LC08/isolation.md
      kind: fixture-evidence
    budget:
      path: LC08/budget.md
      kind: fixture-evidence
    successor_dispatch:
      path: LC08/successor_dispatch.md
      kind: dispatch
    issue:
      path: LC08/issue.md
      kind: rework
    control:
      path: LC08/control.md
      kind: control-state
    task:
      path: LC08/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  successor:
    expected_admission: ready
    requested_resource_ids:
    - OBJ-A
    origin_artifact_digest: 372975bdeef790c22a77f4ab1eb821a80d3561c8eecfd29a1a9aca956fc21c64
    previous_consumed: 7
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
- case_id: LC09
  identity:
    task_id: LC09-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: interrupted
  expected_phase: do
  records:
    source:
      path: LC09/source.md
      kind: fixture-evidence
    baseline:
      path: LC09/baseline.md
      kind: baseline
    plan_request:
      path: LC09/plan_request.md
      kind: request
    plan_message:
      path: LC09/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC09/plan_response.md
      kind: response
    plan_decision:
      path: LC09/plan_decision.md
      kind: request-decision
    commit:
      path: LC09/commit.md
      kind: fixture-evidence
    gate:
      path: LC09/gate.md
      kind: gate-check
    transition1:
      path: LC09/transition1.md
      kind: transition
    stop-source:
      path: LC09/stop-source.md
      kind: fixture-evidence
    order:
      path: LC09/order.md
      kind: fixture-evidence
    stop:
      path: LC09/stop.md
      kind: control-event
    operation:
      path: LC09/operation.md
      kind: operation
    revocation:
      path: LC09/revocation.md
      kind: fixture-evidence
    handoff:
      path: LC09/handoff.md
      kind: fixture-evidence
    effect-proof:
      path: LC09/effect-proof.md
      kind: fixture-evidence
    reservation:
      path: LC09/reservation.md
      kind: resource-reservation
    termination:
      path: LC09/termination.md
      kind: termination
    old-artifact:
      path: LC09/old-artifact.md
      kind: fixture-evidence
    successor_task:
      path: LC09/successor_task.md
      kind: task
    successor_control:
      path: LC09/successor_control.md
      kind: control-state
    issue:
      path: LC09/issue.md
      kind: rework
    control:
      path: LC09/control.md
      kind: control-state
    task:
      path: LC09/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  successor:
    expected_admission: blocked
    requested_resource_ids:
    - OBJ-A
    origin_artifact_digest: c2087b8164bb7d0cd19b6c45427c9dbeccc36d0397d91cd0ab2e38d1a7c65403
    previous_consumed: 7
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
- case_id: LC10
  identity:
    task_id: LC10-OLD
    work_id: W-LC
    tree_revision: TR-LC
    node_id: NODE-LC
    scene: ontology_modeling
    attempt: 1
  expected_state: interrupted
  expected_phase: do
  records:
    source:
      path: LC10/source.md
      kind: fixture-evidence
    baseline:
      path: LC10/baseline.md
      kind: baseline
    plan_request:
      path: LC10/plan_request.md
      kind: request
    plan_message:
      path: LC10/plan_message.md
      kind: fixture-evidence
    plan_response:
      path: LC10/plan_response.md
      kind: response
    plan_decision:
      path: LC10/plan_decision.md
      kind: request-decision
    commit:
      path: LC10/commit.md
      kind: fixture-evidence
    gate:
      path: LC10/gate.md
      kind: gate-check
    transition1:
      path: LC10/transition1.md
      kind: transition
    stop-source:
      path: LC10/stop-source.md
      kind: fixture-evidence
    order:
      path: LC10/order.md
      kind: fixture-evidence
    stop:
      path: LC10/stop.md
      kind: control-event
    operation:
      path: LC10/operation.md
      kind: operation
    revocation:
      path: LC10/revocation.md
      kind: fixture-evidence
    handoff:
      path: LC10/handoff.md
      kind: fixture-evidence
    effect-proof:
      path: LC10/effect-proof.md
      kind: fixture-evidence
    reservation:
      path: LC10/reservation.md
      kind: resource-reservation
    termination:
      path: LC10/termination.md
      kind: termination
    old-artifact:
      path: LC10/old-artifact.md
      kind: fixture-evidence
    successor_task:
      path: LC10/successor_task.md
      kind: task
    successor_control:
      path: LC10/successor_control.md
      kind: control-state
    successor-auth:
      path: LC10/successor-auth.md
      kind: fixture-evidence
    spawn:
      path: LC10/spawn.md
      kind: fixture-evidence
    isolation:
      path: LC10/isolation.md
      kind: fixture-evidence
    budget:
      path: LC10/budget.md
      kind: fixture-evidence
    successor_dispatch:
      path: LC10/successor_dispatch.md
      kind: dispatch
    issue:
      path: LC10/issue.md
      kind: rework
    control:
      path: LC10/control.md
      kind: control-state
    task:
      path: LC10/task.md
      kind: task
  transition_roles:
  - transition1
  operation_roles:
  - operation
  required_operation_ids:
  - OP1
  reservation_roles:
  - reservation
  required_resource_ids:
  - OBJ-A
  successor:
    expected_admission: ready
    requested_resource_ids:
    - OBJ-B
    origin_artifact_digest: 22c98286a90ac4c8be1ab8dffe93f37c7131004c76cf70a772f41ef7d6bdcf48
    previous_consumed: 7
  required_resource_keys:
    OBJ-A:
      backend: fixture
      namespace: lc
      canonical_object_id: OBJ-A
      scope: whole_object
production_eligible: false
---

独立固定的维护验收依据；原始材料在lifecycle目录。测试变体不得修改本basis。所有来源是fixture。
