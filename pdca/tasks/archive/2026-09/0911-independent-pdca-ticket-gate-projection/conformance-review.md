# T2179 Ontology Conformance Review 1

## Review Basis

- Ontology: `ontology:concept/pdca-task`
- Contract: T2179 `task.json#meta.execution_contract`
- Acceptance criteria: T2179 PRD AC-1 through AC-5
- Persisted evidence: `t2179-gate-runtime`, `t2179-ticket-tests`, `t2179-verification-report`, `convergence-map`

## Result

Status: failed; remain in Do.

`TICKETS_MISSING` and its parent-leaf exception were removed, but `scripts/pdca_core.py::_research_first_ok` still traverses `task.children` and accepts another task's archive state as the current task's Plan-to-Do evidence. This makes `children` participate in lifecycle admission and conflicts with:

- AC-2: `parent`, `children`, and `dependencies` are scheduling/decomposition information only.
- `ontology:concept/pdca-task`: each PDCA task is an independent lifecycle; cross-task inspection is forbidden.

## Required Correction

- Stop traversing or indexing related tasks in `_research_first_ok`.
- Research admission, where still applicable, may inspect only the current task's own persisted research artifact.
- Replace the archived-child success regression with a rejection case proving another task's archive state cannot satisfy the current task gate.
- Add `tests/test_research_first_gate.py` as a direct test seam and rerun the targeted Plan gate suite.
- Replace superseded code, test, validation, and convergence evidence through `register-evidence`; keep exactly one active convergence-map.

The broader unrelated fixture failures remain diagnostic only, but all tests directly exercising modified admission behavior must pass before Check.
