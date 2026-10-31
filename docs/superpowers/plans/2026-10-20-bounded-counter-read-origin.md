# Bounded Counter Read-Origin Clarification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new bounded-counter ontology candidate that explicitly maps each `legal_count_value` payload to the corresponding `read()` return value and rules out direct state reads.

**Architecture:** Preserve candidate-0.4.0 byte-for-byte and create candidate-0.5.0 as its successor. Clarify the relation interface contract and C-LABEL-INPUT predicate/observation signals, then update the ontology navigation and the OpenCode evaluation note with the synthetic TUI evidence and its limits.

**Tech Stack:** Markdown with YAML front matter; Ruby YAML parsing and Git inspection for generic validation.

**Spec:** `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.4.0/model.md`, `ontology/concept/ontology-asset.md` (ONTOLOGY-01), and `docs/reviews/2026-10-20-opencode-ai-usefulness.md`.

## Global Constraints

- Keep `fixed_by_modeling_act: false` and `status: candidate`; this maintenance update is not a formal Modeling Act.
- Preserve candidate-0.4.0 and its content unchanged.
- State that `legal_count_value` carries the exact return value of its corresponding `INST-COUNTER.read()` invocation; wrappers may carry provenance but may not re-read internal counter state.
- Keep test/observation signals separate from ontology properties and relations.
- Keep the OpenCode fresh-recovery and child-context smoke inputs aligned with candidate-0.5.0 and assert the exact read-origin contract; this remains an AI behavior diagnostic and cannot upgrade formal H/CAP status.
- Keep the TUI exercise labeled agent-simulated; do not upgrade H1–H18 or CAP-01 from `NOT_RUN`/`unknown`.
- Do not create a formal task, commit, or write business code into the central repository.

---

### Task 1: Create candidate-0.5.0 with explicit read-origin semantics

**Files:**
- Read: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.4.0/model.md`
- Read: `ontology/concept/ontology-asset.md`
- Create: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.5.0/model.md`

**Interfaces:**
- The `REL-CONSUMES-LEGAL-READING` contract defines the formatter payload as the exact value returned by one corresponding `INST-COUNTER.read()` invocation.
- `C-LABEL-INPUT` requires every formatter input to correlate to that read invocation, remain in `[0,2]`, and have no direct counter-state bypass.

- [x] **Step 1: Preserve the base and identify its blob.** Run `git hash-object ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.4.0/model.md`; record the output as `base_candidate_blob` without modifying the base.
- [x] **Step 2: Create the successor candidate.** Copy candidate-0.4.0 to candidate-0.5.0; update `model_root_id`, `revision`, heading, `base_candidate_ref`, and `base_candidate_blob`. Keep all other identities and semantics unchanged except the relation/interface wording and C-LABEL-INPUT wording/signals.
- [x] **Step 3: Add the semantic mapping.** Under `REL-CONSUMES-LEGAL-READING`, state that for each formatting operation the interface payload equals the return value of its corresponding single `read()` invocation; a wrapper may add provenance but must carry that value unchanged and must not re-read counter state.
- [x] **Step 4: Strengthen C-LABEL-INPUT.** Require one-to-one read/formatter correlation and exact value equality. Specify source/call-path review plus runtime observations pairing read invocation, returned value, formatter invocation, and input. State that object identity alone does not prove read provenance. Retain the out-of-range negative case and unknown limitation.
- [x] **Step 5: Validate the candidate structure.** Parse only the YAML front matter, compare its base reference/hash to candidate-0.4.0, and inspect the relation, constraint, provenance, and unknown sections against ONTOLOGY-01. Do not use a project-specific semantic validator.

### Task 2: Record the TUI evidence and point navigation at the successor

**Files:**
- Modify: `ontology/README.md`
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`
- Modify: `.github/workflows/opencode-smoke.yml`

**Interfaces:**
- The README identifies candidate-0.5.0 as the current candidate while preserving the evolution history and non-fixed status.
- The review note records the synthetic TUI scenario, observed capability gate, coding exercise, independent review, RED/GREEN fix, test result, and remaining limits.
- The smoke workflow sources candidate-0.5.0 and requires fresh sessions to recover exact read-return mapping and child context to preserve the same contract.

- [x] **Step 1: Update ontology navigation.** Extend the bounded-counter candidate history with candidate-0.5.0 and state its read-origin clarification; do not remove the candidate-0.4.0 reference.
- [x] **Step 2: Append the synthetic TUI findings.** Record OpenCode v2.0.32, agent-controlled tmux input, the missing-binding stop, CAP-01/CONFIRM-01 task-creation block, the scratch-only Python exercise, its corrected read-origin defect, 17 passing tests, and the fact that no formal task or H item passed.
- [x] **Step 3: Align the OpenCode smoke.** Source ontology core and the pre-H18 child-context fixture from candidate-0.5.0; assert the one-read/one-label, unchanged payload, legal range, and no-bypass/re-read contract in both model probes.
- [x] **Step 4: Check scope and wording.** Confirm the new review section distinguishes actual local observations from formal host evidence and leaves the earlier CLI evaluation intact.

### Task 3: Final generic verification

**Files:**
- Verify: the new candidate, README, review note, and current Git worktree.

**Interfaces:**
- YAML front matter parses; candidate identity and base hash resolve; no `fixed` or H-pass claim is introduced.
- The workflow syntax and embedded response parsers validate; real model output is checked where the configured host permits it, with unavailable model probes reported as unknown.
- `git diff --check` is clean for tracked changes, and Git status shows only the pre-existing work plus the explicitly added candidate/review/plan/binding artifacts.

- [x] **Step 1: Run `git diff --check` and inspect `git status --short`.** Do not stage or commit.
- [x] **Step 2: Parse the new model front matter and verify candidate-0.4.0 remains unchanged.** Report any limitation rather than inferring semantic PASS from syntax checks.
