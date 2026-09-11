# T2181 Ontology Conformance Review

## Review cycle 1

- reviewer: coordinator
- scope: current T2181 task, persisted artifacts, registered evidence, and T2181 implementation surfaces only
- outcome: failed
- phase decision: remain in `do`

## Findings

### F1 - Critical: conformance is self-approved by deterministic checks

`pdca_runtime.lifecycle.resume_for_conformance` writes a review bundle with `result: passed` and immediately appends `conformance_verified`. Evidence presence, digest integrity, AC labels and projection structure cannot prove the semantic chain “ontology definition -> implementation behavior -> evidence”. This lets implementation code certify itself before the coordinator performs the required review.

Required correction: resume must only build a content-addressed review bundle in a pending state. A separate coordinator decision command must record `confirmed` or `rejected`, reason and review digest before the receipt state becomes completed or failed. The bundle must preserve the task's `ontology_projection` role and identify `ontology_conformance_verification` as the review action, not silently replace the task role.

### F2 - High: authoritative graph and bounded subgraph are the same caller-selected set

`build_projection_manifest` constructs `authoritative_ontology_graph` only from caller-provided `--authority` paths. The T2181 manifest reports 6 authority nodes and 6 bounded nodes, so it does not demonstrate the required “authoritative ontology graph -> bounded task subgraph” projection and can omit authority nodes before bounding.

Required correction: construct the authority layer from the active ontology graph under `ontology/` (or a deterministic validated graph index), then select the task's explicit six-node bounded subgraph. T2181 must demonstrate a materially larger authority layer and verify source digests during conformance resume.

### F3 - High: current-task confinement is incomplete

Context validation blocks another `pdca/tasks/*` path but accepts `records/<other-task>/...`. CLI `--bindings` and output paths are not confined to the current task directory, so a caller can read another task's binding document or write projection/context/request artifacts outside the current task.

Required correction: reject every other task record, archived task and task-scoped artifact. Confine bindings and all generated runtime files to the current task directory. Ontology/config/source authority inputs may remain repository-scoped only where explicitly allowed by the command contract. Add negative tests for another record, archive path, external output and external binding input.

### F4 - High: awaiting-confirmation has no persisted resume handshake

The state machine can enter `awaiting_confirmation`, but it has no `user_confirmation_recorded` event or command that binds a real `clarifications.jsonl` confirmation and returns the same bound Agent to an autonomous waiting state. Allowing `agent_completed` directly from `awaiting_confirmation` does not prove that the user response was recorded or made reachable to the Agent.

Required correction: add a coordinator-only confirmation receipt that binds the current task clarification entry/digest and transitions back to `suspended_waiting_agent` (or an equivalently explicit resume-ready state). Completion after an unresolved confirmation request must be rejected. Add positive and forged/missing confirmation tests.

### F5 - Medium: baseline comparison evidence mixes test runners

The Plan baseline used `python3 -m unittest discover -s tests` and observed 261 tests, 37 failures, 5 errors and 2 skips. The Do report's final 48/375/3 numbers are from pytest, so they cannot be compared directly. The claimed pre-edit pytest 70-failure set is not preserved as registered raw evidence.

Coordinator reran the original unittest command after Do and observed 260 tests, 24 failures, 1 error, with the same known failure families and no count increase. This supports improvement but does not validate the report's unregistered 70-failure identity claim.

Required correction: distinguish unittest and pytest observations, remove unsupported “strict subset of 70” claims unless the raw pre-edit list is persisted, and record a same-runner comparison. All target tests for F1-F4 must pass.

### F6 - Low: generated cache files remain in the new runtime directory

`pdca_runtime/__pycache__/` exists as ignored local output. It is not part of the Git change set, but it should not be treated as a work product or evidence input.

Required correction: exclude generated caches from all manifests and reports; removal is optional housekeeping and must not affect source evidence.

## Re-entry conditions

The same T2181-bound Agent may perform one autonomous correction round using this persisted review. The coordinator must not implement the fixes. After correction, evidence replacement must preserve cycle-1 history, convergence must still validate, and T2181 must remain in Do for a second coordinator conformance review.

## Review cycle 2

- reviewer: coordinator
- scope: current T2181 task, persisted artifacts, registered evidence, and T2181 implementation surfaces only
- outcome: failed
- phase decision: remain in `do`

## Cycle 2 findings

### F7 - High: conformance decision accepts stale reviewed inputs

`resume_for_conformance` correctly creates a content-addressed pending bundle, but `record_conformance_decision` only revalidates the bundle file and its digest. It does not revalidate the task, receipt log, transition receipts, evidence manifest, work products, or projection sources recorded by that bundle. A coordinator can therefore prepare a review, mutate a bound work product, and still record `confirmed`; the runtime returns `completed`.

Required correction: while holding the current-task lock, revalidate every input digest in the pending bundle and rerun projection source verification immediately before appending the decision receipt. Any task, receipt, transition, evidence, work-product, projection, or authority-source drift must fail closed with a stable error and leave the execution state awaiting conformance verification. Add focused negative tests, including work-product and evidence drift after bundle creation.

### F8 - High: affected migration regressions are still red

The correction report marks AC-10 passed but an independent run of the declared/affected seams
`tests/test_operations.py`, `tests/test_execution_and_invocation_contracts.py`,
`tests/test_research_first_gate.py`, and `tests/test_convergence.py` reports
6 failures and 30 passes. Three transition fixtures fail after their scenario-to-role migration because they no longer satisfy the current Plan gate contract; three convergence fixtures fail because `ontology_exempt=true` lacks the schema-required reason. These files are part of the migration surface, so a lower repository-wide failure count cannot classify them as passing affected regressions.

Required correction: update only the T2181-migrated fixtures or implementation contract needed by these seams, then make the four-file command pass. Persist the raw command output. Replace the count-only AC-10 claim with an identity table that separates T2181-owned failures from unrelated baseline failures; no modified or explicitly declared T2181 seam may remain red.

### F9 - Medium: projection relation vocabulary is hardcoded and graph counts are conflated

`pdca_runtime.projection.RELATION_KEYS` duplicates the seven relation keys already governed by `ontology:concept/ontology-rule-non-dangling`. This means a future ontology rule change can produce a newly built projection that silently ignores the new governed relation, contrary to the ontology-driven core. The runtime currently projects 1629 governed semantic edges, while `scripts/ontology_graph.py` reports 1727 because that visualization script also treats 98 `relations.testable_signal` entries as graph edges. The validation report calls both results the authority graph without explaining the different semantics.

Required correction: derive the projection relation vocabulary from the active ontology rule node and fail closed when its rule specification is missing or invalid. Add a test proving rule-driven relation selection. Report the runtime governed-edge count separately from the legacy visualization count; do not claim both as the same graph edge count.

## Cycle 2 re-entry conditions

The same T2181-bound Agent may perform correction cycle 2 from this persisted review. It must preserve prior evidence through replacement records, keep the task in Do, and produce a new completion marker for coordinator review cycle 3. It must not write a Check conclusion, verdict, user confirmation, disposition, journal entry, or phase transition.
