# Plan: Preserve unresolved persistence scope in bounded-counter ontology

## Goal

Create an immutable `candidate-0.7.0` successor that preserves the source seed phrase “无持久化的示例” as an unresolved scope item. Prevent OpenCode's fresh-core compatibility probe from claiming full requirement coverage while that item is unresolved. Demonstrate the current 0.6 answer fails the new response contract, run two fresh OpenCode sessions against 0.7 and require equivalent normalized semantics, then close the child-probe gap where free-text output named identifiers absent from its context.

## Architecture

- Keep `candidate-0.6.0` byte-for-byte unchanged; derive 0.7 from its current blob.
- Represent the phrase with one source-preserving uncovered coverage row and one unknown that records the missing subject, whether it is a behavior constraint or sample-scope description, evidence needed, impact, and resolution condition.
- Do not invent a non-persistence constraint, mark the source item not applicable, or claim all source requirements are covered.
- Extend the existing fresh-core model response and parser with a required `scope_coverage` object. The exact expected response is:

  ```json
  {
    "uncovered_requirements": ["REQ-SCOPE-001"],
    "unknowns": ["U-PERSISTENCE-SCOPE"],
    "all_requirements_covered": false,
    "persistence_semantics_resolved": false
  }
  ```

- Update the workflow's candidate revision and generated child-context labels consistently. Keep the unresolved scope visible in both probes. The label-child context must state that this root-scope unknown blocks a root-level coverage claim and that its impact on local label scope remains unknown; it must not silently classify the phrase out of context.
- The child-context output parser must reject any ontology identifiers used in response strings that do not occur in the supplied child context. The prompt must tell the model not to reconstruct omitted identifier names or semantics.
- Record the maintenance finding and evidence without changing formal task, Modeling Act, implementation, H1–H18, CAP-01, or human-origin status.

## Tech Stack

Markdown ontology artifacts, Git blob hashing, GitHub Actions YAML, embedded Bash/Python, OpenCode CLI fresh sessions, PyYAML, Bash syntax checking, ShellCheck, Python AST parsing.

## Spec

1. Candidate metadata identifies a unique 0.7 model root, points to the exact candidate-0.6.0 blob as its base, and remains `status: candidate` / `fixed_by_modeling_act: false`.
2. Candidate 0.7 preserves all existing 0.6 semantics and adds only traceability for the unresolved persistence phrase; it contains no persistence behavior constraint or unsupported applicability decision.
3. The source phrase is represented in Requirement Coverage as `REQ-SCOPE-001` with state `uncovered`, and in Unknowns as `U-PERSISTENCE-SCOPE` with explicit unresolved question, missing evidence, impact, and resolution condition.
4. Global coverage and semantic-closure statements clearly limit the covered claim to the other six requirements and disclose the unresolved source item.
5. Workflow prompt/schema/parser require the exact scope coverage object and include it in normalized semantics. Existing candidate 0.6 OpenCode output must fail the updated parser because the new field is absent.
6. Two distinct fresh OpenCode sessions on the updated core must parse successfully, report the unresolved item, and produce identical normalized semantics.
7. All candidate references and test-only child-context references in the workflow and ontology README point to 0.7 where they describe the current candidate. Candidate 0.6 remains unchanged.
8. The previous child response pair is rejected by the strengthened parser because its free-text limitations contain identifiers absent from the supplied child context; at minimum the known false `C-LABEL-001` and `C-COMP` identifiers are detected.
9. Two new fresh child sessions parse successfully with distinct IDs, equal normalized semantics, the same root-scope boundary, and no ontology identifier absent from their supplied context.
10. The review clearly states that the first child pair passed the original structural parser but manual raw-answer inspection found unsupported identifiers, and records the regression and corrected follow-up separately.

### Exact model values

- New coverage row: `REQ-SCOPE-001`; statement: `Seed scope clause “无持久化的示例”; its subject and behavioral meaning are unresolved.`; coverage: `uncovered`; carried by: `U-PERSISTENCE-SCOPE`.
- New unknown: `U-PERSISTENCE-SCOPE`.
  - subject: source-scope clause `REQ-SCOPE-001` from `SRC-USER-SEED`.
  - unresolved question: whether “无持久化的示例” states a behavioral persistence constraint, and if so which state/lifecycle it governs, or whether it only describes the sample scope.
  - missing evidence: authoritative source/user clarification identifying the subject and intended meaning; if behavioral, the persistence boundary and observable signal are also missing.
  - impact: keep `REQ-SCOPE-001` uncovered; do not infer a `C-NO-PERSIST`; no full source-coverage/root semantic-closure claim is allowed; impact on individual child-node scope remains unknown.
  - resolution condition: obtain authoritative clarification; if behavioral, define the persisted subject, lifecycle boundary, and observable signal before adding a constraint; otherwise record the explicit scope exclusion and rationale in a successor.
- New provenance entry: `SRC-PERSISTENCE-SCOPE-REVIEW`, kind `maintenance_review`, source `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-persistence-scope-coverage-gap`, repository `MyBlackHole/pdca-workflow`, commit `138451df49a9f01d0b7a65a92921210b4c41fa68` (rules baseline only). It records that 0.6 omitted this phrase while claiming coverage; it must explicitly say the review does not resolve the phrase's semantics or establish host/user evidence.
- The candidate identity changes to `candidate-0.7.0`; root id/ref/revision/title all use 0.7.0; `base_candidate_ref` points to candidate 0.6.0 and `base_candidate_blob` is `f19bcb8cea1d571b03555d64413c2c81b37d33ce`; the dependency interface revision becomes `legal_count_value@candidate-0.7.0`.
- README summary names 0.7 as current, states it records the unresolved source clause without inventing persistence semantics, and keeps 0.6 historical/unchanged.
- Child-context scope boundary exact value is the `root_scope_boundary` object specified in Task 1.

## Global Constraints

- This is repository maintenance and compatibility-probe work, not a formal PDCA task or phase.
- Do not fabricate user, host, task, Agent, approval, or lifecycle evidence; do not mark H1–H18 or CAP-01 PASS.
- Preserve unrelated pre-existing worktree changes. Do not stage or commit.
- Store raw OpenCode diagnostic evidence only under `/tmp`, mode `0600`; record that model prompts and responses are synthetic Agent evidence.
- If public-model services are unavailable, report the concrete failure and retain the static / parser evidence; do not claim the fresh-session verification passed.

## Tasks

### Task 1 — Extend the fresh-core OpenCode response contract

**Files:** `.github/workflows/opencode-smoke.yml`

First run a focused validation against the stored candidate-0.6 response that fails because it has no `scope_coverage` field. Then add the `scope_coverage` contract to the core prompt, expected response validation, and normalized semantics. Update the core extraction input/output and child-context revision to candidate 0.7. Add the explicit unresolved root-scope boundary to the child-context prompt and parser without asserting that the unknown does or does not apply to local label behavior. Preserve all existing unrelated probes.

Core JSON field `scope_coverage` must equal:

```json
{
  "uncovered_requirements": ["REQ-SCOPE-001"],
  "unknowns": ["U-PERSISTENCE-SCOPE"],
  "all_requirements_covered": false,
  "persistence_semantics_resolved": false
}
```

The label-child JSON field `root_scope_boundary` must equal:

```json
{
  "uncovered_requirement": "REQ-SCOPE-001",
  "unknown": "U-PERSISTENCE-SCOPE",
  "root_coverage_blocked": true,
  "local_label_impact": "unknown"
}
```

**Verification:** Run the updated parser against an existing 0.6 response and record the expected missing-field failure. Then run Bash, ShellCheck, YAML, and Python heredoc syntax validation for the changed workflow.

### Task 2 — Add candidate 0.7 and update ontology navigation

**Files:** `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.7.0/model.md`, `ontology/README.md`

Copy candidate 0.6 into a new immutable successor, verify the 0.6 base blob first, update candidate identity and interface revision, add the unresolved source coverage item and unknown, add review provenance, and qualify all coverage/self-review claims. Update the README's current candidate pointer and revision summary.

Use these exact model values:

- `REQ-SCOPE-001` statement: `Seed scope clause “无持久化的示例”; its subject and behavioral meaning are unresolved.`; coverage `uncovered`; carried by `U-PERSISTENCE-SCOPE`.
- `U-PERSISTENCE-SCOPE`: subject is the source-scope clause `REQ-SCOPE-001` from `SRC-USER-SEED`; unresolved question is whether “无持久化的示例” states a behavioral persistence constraint and, if so, which state/lifecycle it governs, or whether it only describes the sample scope; missing evidence is authoritative source/user clarification identifying the subject and meaning, plus persistence boundary and observable signal if behavioral; impact is that the requirement remains uncovered, no `C-NO-PERSIST` may be inferred, full source-coverage/root semantic closure cannot be claimed, and child-node impact remains unknown; resolution requires authoritative clarification, then either defining persisted subject/lifecycle/observation before adding a constraint or recording an explicit scope exclusion and rationale in a successor.
- Provenance ID `SRC-PERSISTENCE-SCOPE-REVIEW`; kind `maintenance_review`; source `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-persistence-scope-coverage-gap`; repository `MyBlackHole/pdca-workflow`; commit `138451df49a9f01d0b7a65a92921210b4c41fa68` (rules baseline only); intent is to record that 0.6 omitted this source phrase while claiming coverage; limitation says this review does not resolve its semantics or establish host/user evidence.
- Identity values: model root ID `project-ontology:pdca-host-smoke/bounded-counter@candidate-0.7.0`; model root ref `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.7.0/model.md`; revision/title `candidate-0.7.0`; base ref `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.6.0/model.md`; base blob `f19bcb8cea1d571b03555d64413c2c81b37d33ce`; dependency interface revision `legal_count_value@candidate-0.7.0`.
- Preserve `status: candidate`, `fixed_by_modeling_act: false`, `protocol_revision: 4.0.0-rc.5`, and `payload_scope: this_model_root_file`.
- README must name 0.7 as current and say it records the unresolved source clause without inventing persistence semantics; 0.6 remains historical and unchanged.

**Verification:** Verify the candidate base blob, current metadata, exact unchanged 0.6 blob, and absence of an invented persistence constraint or `not_applicable` resolution.

### Task 3 — Run fresh-session verification and record the review

**Files:** `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

Run two new OpenCode public free-model sessions using the exact updated workflow prompt, extracted 0.7 ontology core, and exact embedded parser, then run two fresh child-context sessions using the updated child fixture/parser. Execute the workflow's `fresh_recovery` and `child_context` run blocks locally with PyYAML extraction, a temporary HOME that exposes this checkout's PDCA skills, and a private temp directory `/tmp/pdca-persistence-scope-20261020` (`umask 077`). Use `opencode run --format json` and fresh invocations; do not reuse/resume a session. Require distinct session IDs per pair, equal normalized semantics per pair, and explicit preservation of the unresolved persistence item in both scopes. Keep JSONL, stderr, prompts, and summaries mode `0600`; raw diagnostics stay in `/tmp`. Record OpenCode version/model/session IDs, exact parser results, artifact paths, and synthetic-agent-evidence limitation in the review.

Append the evidence under the exact heading `### 2026-10-20 persistence scope coverage gap` so the candidate provenance link resolves. State explicitly that the probe is synthetic and cannot mark formal PDCA, host, H1–H18, CAP-01, or human-origin evidence PASS.

**Verification:** Run static validation, Git diff checks, candidate/hash checks, and confirm H1–H18 remain `NOT_RUN` and no files are staged.

### Task 4 — Reject identifiers absent from the child context

**Files:** `.github/workflows/opencode-smoke.yml`, `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

Before editing, parse the saved child run-1 response and child fixture to demonstrate RED: one or more identifier-like references in model-written strings are absent from the fixture. Then update the child prompt to prohibit reconstructing omitted identifiers or semantics, and update the child parser to extract the identifiers available in the exact fixture and reject response strings containing any identifier outside that set. Check the whole returned JSON, including `responsibility` and `limitations`; do not weaken the existing expected-field, scope-boundary, exclusion, or tool-boundary checks.

Run the strengthened parser against the saved Task 3 child pair and record the expected rejection. Then run two new fresh OpenCode child sessions with the exact current workflow block and parser. Require distinct session IDs, identical normalized semantics, the exact `root_scope_boundary`, and no unsupported identifier references. Add the initial output defect and correction results to the existing review section. If the new model calls still include unsupported identifiers, report the remaining failure instead of claiming green.

**Verification:** Run Bash, ShellCheck, YAML, and Python heredoc validation for the changed workflow; verify the old child response is RED, the new response pair is GREEN, evidence permissions remain private, H1–H18 stay `NOT_RUN`, and no files are staged.

### Task 5 — Enforce exact JSON types and identifier coverage

**Files:** `.github/workflows/opencode-smoke.yml`, `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

Before editing, extract the current embedded core and child parsers and mutate saved responses at the existing JSONL parser seam. Demonstrate that the current core parser accepts numeric `0` in place of the two `false` values in `scope_coverage`; that the current child parser accepts numeric `1` in place of `root_coverage_blocked:true`; that an out-of-context identifier placed in a JSON object key inside `limitations` is missed; and that a non-string `limitations` item is accepted when its nested key is in the fixture. Record these acceptance failures as RED evidence under private `/tmp` storage.

Update the core parser to require actual JSON booleans for the two `scope_coverage` boolean fields before normalization. Update the child parser so recursive identifier scanning covers both dictionary keys and values, and require `limitations` to be a nonempty list of nonempty strings. Preserve the existing field, scope-boundary, exclusion, tool-boundary, and normalized-semantics checks.

Run the strengthened parsers against all four malformed saved-response variants and require rejection for the specific malformed field. Re-run the parser on the valid saved fresh-core pair and valid Task 4 retry child pair; both must pass unchanged. Add the final-review finding and fix results to the review record. Do not launch additional model calls; the parser input/output seam is the exact workflow block and saved JSONL used by prior tasks.

**Verification:** Run Bash, ShellCheck, YAML, and Python heredoc validation for the changed workflow; confirm all malformed cases are rejected for the intended reason, valid saved pairs remain GREEN, evidence permissions are private, candidate 0.6 remains unchanged, H1–H18 remain `NOT_RUN`, and no files are staged.
