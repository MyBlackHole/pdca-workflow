# T2179 Do Verification Report

## Scope

This report verifies the corrected independent-task Plan-to-Do gate projection after conformance review 1. It does not advance the task to Check and does not provide a conclusion or verdict.

## Implemented Changes

- `scripts/pdca_core.py`: removed the complete `TICKETS_MISSING` branch, including the parent leaf exemption and the child-ticket guidance text.
- `scripts/pdca_core.py`: removed `_task_index` and all traversal of `children` or related task archive state from `_research_first_ok`; research admission now reads only the current task's persisted `research-report.md`.
- `tests/test_tickets_gate.py`: replaced the old parent-leaf control expectations with parentless, `children=[]`, `dependencies=[]` coverage for `ontology_modeling`, `ontology_projection`, and `ontology_conformance_verification`.
- `tests/test_research_first_gate.py`: replaced the archived-related-task success expectation with a blocking regression, while retaining the current-task passing-report success case.
- Existing final confirmation, Grill, ontology-ready, PRD, evidence, convergence, and phase-transition branches were not edited by T2179.
- `tests/test_gate_negative.py` was not edited by T2179 because it does not exercise the ticket admission seam.

## Acceptance Evidence

- AC-1: each independent role fixture reaches the Plan gate with no issues when all other inputs are valid.
- AC-2: Plan admission no longer indexes tasks or reads `parent`, `children`, `dependencies`, or another task's archive state; only the current task's persisted research artifact can satisfy research admission.
- AC-3: one parameterized test executes all three ontology roles as separate subtests.
- AC-4: selected current regressions cover final confirmation rejection, research gating, ontology-ready checks, and legal adjacent transition semantics.
- AC-5: `rg` found no `TICKETS_MISSING`, old child-ticket message, `is_leaf`, or old parent-leaf test names under `scripts/` and `tests/`.

## Verification Results

1. `python3 -m pytest -q tests/test_research_first_gate.py tests/test_tickets_gate.py`
   Result: PASS, 6 tests passed with 3 subtests. The archived related task is rejected and the current task's passing report is accepted.
2. `python3 -m pytest -q tests/test_tickets_gate.py tests/test_research_first_gate.py tests/test_gate_compliance.py::GateRejectionLeakTest::test_rejected_receipt_written_on_final_confirmation_missing tests/test_ontology_reason.py::test_gate_missing_fragment tests/test_ontology_reason.py::test_gate_valid_fragment tests/test_ontology_reason.py::test_reason_legal_meta_present`
   Result: PASS, 10 tests passed with 3 subtests.
3. Static forbidden-branch scans for `TICKETS_MISSING`, `_task_index`, archived-child guidance, and the old parent-leaf controls.
   Result: PASS, no matches.
4. `git diff --check`
   Result: PASS, no whitespace errors.

## Extended Diagnostics

The broader mixed regression command completed with 34 passed, 7 passed subtests, and 10 failures. Those failures concern stale fixtures for research/Grill, ontology exemption reason, disposition, doctor state, and the existing `ILLEGAL_TRANSITION` versus `NON_ADJACENT_TRANSITION` expectation; none exercises the removed ticket branch.

`tests/test_gate_negative.py` completed with 5 passed and 2 failures because `check-design-vocab.py` produced no JSON for two design-vocabulary cases. The file already contained an unrelated pending default-role change and was left untouched.

The full AI-friendliness fixture harness reported 11 of 22 passing; its failures concern pre-existing scenario/invocation/lifecycle fixture migration. These diagnostics are reported as repository state and are not treated as passing T2179 evidence.
