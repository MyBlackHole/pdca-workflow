# Counter Read Observation Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure the bounded-counter model's read observation signal and counter-node oracle reject implementations that return a stable but stale value.

**Architecture:** Preserve candidate-0.5.0 unchanged and create candidate-0.6.0 with explicit current-state and non-mutation observations at values 0, 1, and 2. Extend the existing fresh-core OpenCode probe to recover and parse that contract; retain the label-child minimum context boundary.

**Tech Stack:** Markdown ontology artifact, Git blob inspection, OpenCode CLI, embedded workflow parser, YAML and shell syntax checks.

**Spec:** `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.5.0/model.md`, `ontology/concept/ontology-asset.md` (ONTOLOGY-01), and `tests/host-acceptance.md` (H11/H18 remain formal host acceptance).

## Global Constraints

- Preserve candidate-0.5.0 byte-for-byte; candidate-0.6.0 remains `status: candidate` and `fixed_by_modeling_act: false`.
- Keep derived `NODE-*` identities out of ontology core Sections 1–7.
- C-READ must explicitly compare each read return with the known current value and confirm the counter value is unchanged at 0, 1, and 2, including after reset.
- Keep ontology constraints and observation signals distinct; do not add a project-specific semantic validator.
- Extend the existing OpenCode fresh-core fixture/parser to assert the read observation contract; do not add C-READ implementation details to the label-child minimum context.
- Synthetic CLI/TUI evidence does not change CAP-01 or H1–H18 status.
- Do not create a formal PDCA task, stage changes, or commit.

---

### Task 1: Add the fresh-core regression contract before changing the model

**Files:**
- Modify: `.github/workflows/opencode-smoke.yml`

**Interfaces:**
- C-READ observation: at each counter value 0, 1, and 2, observe `value` before `read()`, require the return to equal it, and observe `value` after `read()` to confirm it is unchanged; repeat after reset at 0.
- NODE-COUNTER oracle: explicitly read and verify the unchanged state at 0, after the first increment to 1, after the second increment to 2, after saturation, and after reset.

- [x] **Step 1: Add the expected observation object.** Extend the fresh-core JSON shape and parser to require `counter_read_observation` with known states `[0,1,2]`, current-value equality, unchanged state after every read, repeated reads at each state, and reset read `0`.
- [x] **Step 2: Verify RED against existing candidate-0.5.0 output.** Extract the current workflow parser and run it on `/tmp/pdca-candidate05-fresh-smoke-value-20261020/cli-run.jsonl` and `cli-run2.jsonl`; expected failure is that both old answers lack the new observation object.

### Task 2: Create candidate-0.6.0 with a discriminating C-READ oracle

**Files:**
- Read: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.5.0/model.md`
- Create: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.6.0/model.md`
- Modify: `ontology/README.md`
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

**Interfaces:**
- Preserve candidate-0.5.0 and record its blob. Use the exact value as candidate-0.6.0's `base_candidate_blob`.
- Copy candidate-0.5.0 and update successor identity/base references, the C-READ observation signal, AC-NODE-COUNTER-3/oracle, provenance for this maintenance finding, and semantic-closure observability summary.
- Point ontology navigation at candidate-0.6.0 while retaining the 0.5 history. Record the mutant result as synthetic maintenance evidence.

- [x] **Step 1: Copy and update candidate-0.6.0.** Keep all unrelated ontology semantics from 0.5 unchanged.
- [x] **Step 2: Verify the successor locally.** Parse its front matter, confirm the 0.5 base blob, inspect the C-READ signal/oracle, and confirm Sections 1–7 contain no `NODE-*` identity.
- [x] **Step 3: Update navigation and evidence.** Point the current-candidate link at 0.6 and record the counterexample without promoting synthetic evidence to formal status.

### Task 3: Switch smoke inputs and verify recovery

**Files:**
- Modify: `.github/workflows/opencode-smoke.yml`

**Interfaces:**
- Fresh-core prompt asks for the new read observation object; parser requires it in both independent sessions and includes it in normalized semantics.
- The label-child context remains limited to NODE-LABEL, its parent boundary, and the required dependency contract; its version references point at candidate-0.6.0.

- [x] **Step 1: Switch smoke inputs to candidate-0.6.0.** Update the core filename, candidate references in the child fixture, and artifact path.
- [x] **Step 2: Run two fresh-core and two child-context OpenCode sessions.** Use the current local OpenCode CLI; extract and run the exact workflow parsers. Require distinct sessions, stable normalized semantics, and no changes to formal readiness status.

### Task 4: Verify candidate lineage and scope

**Files:**
- Verify: candidate-0.5.0, candidate-0.6.0, workflow, review note, ontology navigation, and Git worktree.

- [x] **Step 1: Verify lineage and syntax.** Parse front matter, compare candidate-0.5.0 blob to the new base hash, confirm 0.5 bytes are unchanged, parse workflow YAML, run `bash -n` over every workflow `run` block, run `sh -n install.sh`, and run `git diff --check`.
- [x] **Step 2: Verify authority status remains honest.** Confirm candidate-0.6.0 is unfixed, no formal task was created, and H1–H18 remain `NOT_RUN`.

### Task 5: Exercise the state-sequence observation against scratch implementations

**Files:**
- Copy only under `/tmp/pdca-candidate06-impl-check-20261020/`: the prior scratch implementation, its tests, and candidate model text.
- Modify only the temporary test copy; do not add implementation or test files to the product repository.
- Record diagnostic results in `docs/reviews/2026-10-20-opencode-ai-usefulness.md`.

**Interfaces:**
- At states 0, 1, and 2, `read()` returns the known current value and leaves state unchanged on repeated reads.
- The observation rejects both a constant-zero stale read and a read operation that mutates state.
- These scratch results remain synthetic maintenance evidence, not formal Implement or Verify evidence.

- [x] **Step 1: Add the state-sequence assertion to the isolated test copy.** Check two reads at each known state, state preservation, subsequent increment/saturation, and reset.
- [x] **Step 2: Run the complete scratch suite and both mutants.** The correct implementation passes all 19 tests; constant-zero and state-mutating read mutants are rejected by the new test.
- [x] **Step 3: Record evidence and limits.** Store fresh logs under `/tmp` and describe the diagnostic without changing formal task, candidate, CAP-01, or H1–H18 status.

### Task 6: Generate a fresh scratch implementation with OpenCode and challenge its tests

**Files:**
- Create only under `/tmp/pdca-candidate06-opencode-impl-EymnYj/target/`: a candidate-0.6.0 model copy, `bounded_counter.py`, and `test_bounded_counter.py`.
- Keep session export and test logs under `/tmp/pdca-candidate06-opencode-impl-EymnYj/evidence/`.
- Record results in `docs/reviews/2026-10-20-opencode-ai-usefulness.md`.

**Interfaces:**
- OpenCode receives candidate-0.6.0 Sections 1–7 and synthetic user instructions through an isolated tmux TUI.
- The generated tests must observe the current-state read contract at 0, 1, and 2, read-origin pairing, out-of-range rejection before formatter invocation, and stated Python reflection limits.
- Generated artifacts and mutant trials remain scratch-only; they do not establish formal Implement/Verify, candidate fixation, CAP-01, or H1–H18 acceptance.

- [x] **Step 1: Run OpenCode in the isolated target.** Preserve the session export and confirm all recorded file paths and test commands stay within `/tmp`.
- [x] **Step 2: Run the generated suite independently.** The generated implementation and tests pass all 18 tests.
- [x] **Step 3: Challenge the generated suite with two read mutants.** It rejects constant-zero and state-mutating `read()` copies; retain the separate logs.
- [x] **Step 4: Record interaction quality and authority limits.** Note the transport timeout/follow-up and keep every formal task, candidate, CAP-01, and H1–H18 status unchanged.

### Task 7: Correct the generated implementation's read-origin bypasses

**Files:**
- Modify only the scratch copies under `/tmp/pdca-candidate06-opencode-impl-EymnYj/target/`.
- Record the review and verification in `docs/reviews/2026-10-20-opencode-ai-usefulness.md`.

**Interfaces:**
- `format_count_label` cannot accept a bare integer; `legal_count_value` cannot turn an arbitrary integer into a producer payload.
- The factory receives the counter producer, reads once, range-checks, and preserves that returned integer in an ordinary-API-immutable wrapper.
- Python reflection/token access remains documented as a limitation, not a security boundary.

- [x] **Step 1: Reproduce the public formatter bypass.** The initial code returned `count=1` from `format_count_label(1)` with zero counter reads; the new regression failed for 0, 1, and 2.
- [x] **Step 2: Reproduce the unbound factory and mutable payload paths.** `legal_count_value(1)` minted a payload without a counter read; changing a valid payload's `_value` through `setattr` changed the formatter output from `count=0` to `count=2`.
- [x] **Step 3: Fix and verify in the isolated OpenCode target.** The factory now accepts a producer and reads once; raw values and ordinary wrapper construction are rejected; wrapper attributes are read-only; the final 24-test suite passes.
- [x] **Step 4: Run mutation checks and record authority limits.** The generated suite rejects the constant-zero and read-mutating mutants. No product implementation, formal task, fixed candidate status, CAP-01 result, or H1–H18 status was changed.
