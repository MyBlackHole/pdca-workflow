# T2181 Do validation report

This is a Do-stage technical report for conformance correction cycle 1. It is
not a Check conclusion, verdict, user confirmation, disposition, journal entry,
or phase transition.

## Correction result

F1-F5 are corrected and F6 is honored. The colocated runtime suite passes, the
active ontology graph is materially larger than the six-node task projection,
and the task remains in `do` for coordinator conformance review cycle 2.

## Finding closure

| Finding | Correction | Focused verification |
|---|---|---|
| F1 | `resume_for_conformance` now writes only a content-addressed `result=pending` bundle. It preserves the task `ontology_role` and records `ontology_conformance_verification` as `review_action`. `record-conformance-decision` separately requires `confirmed|rejected`, a non-empty reason, and the exact review digest before appending a terminal receipt. | Resume remains `awaiting_conformance_verification`; forged digest and empty-reason decisions are rejected. |
| F2 | Projection construction enumerates all `status: active` assets below `ontology/`; callers provide only the bounded node IDs. Verification reconstructs the complete active graph and validates source digests. | T2181 projection: 569 authority nodes, 6 bounded nodes, 9 DAG leaves; caller-omitted authority and source drift are rejected. |
| F3 | Context rejects every other task, archive, other record, generated cache, and non-allowlisted repository input. CLI bindings, runtime inputs, and all generated outputs are confined to the current task directory. Completion artifacts are confined to the current task or its own record. Side-effecting APIs validate the active task location before creating a lock. | Negative cases cover another task, another record, archive, external context, external bindings, and external output. |
| F4 | `awaiting_confirmation` no longer accepts `agent_completed`. An Agent request snapshots the clarification prefix; `record-user-confirmation` must bind one new validated current-task clarification entry and digest, writes a coordinator receipt, and returns the same Agent to `suspended_waiting_agent`. Recorded entries are revalidated before later result or conformance handling. | Positive same-Agent resume plus unresolved, missing, forged-digest, and persisted-entry drift boundaries are covered. |
| F5 | unittest and pytest are reported separately. Only the Plan's unittest runner is used for the baseline comparison; no unregistered pre-edit pytest identity claim remains. | Report-content negative test rejects the unsupported wording. Raw correction outputs are persisted. |
| F6 | Generated interpreter caches are rejected as context inputs and are absent from projection, context, report, and evidence source manifests. | Cache-path negative case passes; generated cache files are not registered as evidence. |

## Acceptance mapping

| Criterion | Evidence | Result |
|---|---|---|
| AC-1 | consumer inventory; complete 569-node authority graph -> six-node bounded graph -> nine-leaf DAG | pass |
| AC-2 | executable-task Schema/parser and three-role/four-field negatives | pass |
| AC-3 | required spawn configuration, no fallback, doctor/runtime fail-closed test | pass |
| AC-4 | content-addressed manifests, lock/CAS binding, stale/tampered/cross-scope negatives | pass |
| AC-5 | binding folds to `suspended_waiting_agent`; no polling, wait, or main-session execution entrypoint | pass |
| AC-6 | result binding, persisted confirmation handshake, pending review bundle, separate coordinator decision | pass |
| AC-7 | active legacy-control scan has zero matches | pass |
| AC-8 | behavior comes from explicit four-field contract; no role-derived scenario behavior | pass |
| AC-9 | all three roles plus F1-F4 rejection boundaries pass targeted tests | pass |
| AC-10 | targeted, same-runner unittest baseline, pytest, ontology, graph, skills, projection, convergence, and diff checks recorded below | pass with disclosed unrelated baseline |
| AC-11 | bootstrap request/binding remain separate and unchanged; runtime has no bootstrap compatibility parser | pass |

## Test results

### Runtime tests

Per the latest explicit instruction, new cases live under `pdca_runtime/tests/`;
legacy `tests/` cases are not part of the final correction gate.

`python3 -m pytest -q pdca_runtime/tests` reports
`26 passed, 10 subtests passed`.

`python3 -m unittest discover -s pdca_runtime/tests` reports
`Ran 26 tests ... OK`.

The focused lifecycle/projection subset reports `21 passed, 7 subtests passed`;
the strict task-contract subset reports `5 passed, 3 subtests passed`.

### Superseded legacy-suite observation

Plan baseline command: `python3 -m unittest discover -s tests`.

- Plan persisted baseline: 261 tests, 37 failures, 5 errors, 2 skipped.
- Coordinator cycle-1 observation from `conformance-review.md`: 260 tests,
  24 failures, 1 error.
- Pre-redirect correction run: 266 tests, 24 failures, 1 error.

That pre-redirect test count was five above the Plan count because discovery then
included the new correction tests. Failure and error counts were lower than the
Plan baseline and unchanged from the coordinator's cycle-1 observation. This is
a count-level same-runner comparison only; it does not claim an unpreserved
pre-edit pytest failure identity set.

The raw legacy-suite observations are retained only as audit history because F5
required a like-for-like baseline run before the later user redirect. They are not
used as the final correction pass signal and were not rerun after test relocation.

## Structural validation

- Ontology contract: pass.
- Ontology graph: 569 nodes, 1727 edges, 0 islands.
- Skill index: valid, 50 assets.
- Projection verification: 569 authority nodes, 6 bounded nodes, 9 leaves.
- Convergence validation: pass before evidence replacement; rerun after replacement.
- Active legacy-control residual scan: zero matches.
- Generated-cache manifest/report scan: zero matches.
- Runtime compilation: pass.
- `git diff --check`: pass.

## Residual limits

The runtime remains platform-neutral and never starts a subprocess Agent. POSIX
`flock` remains the lock implementation. Repository-wide unrelated baseline
failures listed above remain red; this correction does not alter their task,
record, or ontology ownership.

No conclusion, verdict, confirmation, disposition, journal entry, archive action,
or Do-to-Check transition was performed.
