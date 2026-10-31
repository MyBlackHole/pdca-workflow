# Candidate 0.9 Operation Semantics Implementation Plan

> **For agentic workers:** Execute inline in the current shared worktree. Do not stage or commit.

**Goal:** Create candidate 0.9.0 that keeps user-seeded state requirements separate from unspecified operation return contracts and unconfirmed label/read interface choices.

**Architecture:** Preserve candidate 0.8.0 byte-for-byte and create 0.9.0 from its exact blob. Record operation returns, read-to-label mapping details, and negative-case observability as explicit unknowns or candidate decisions; update the OpenCode core and label-child prompts/parsers to require that separation; verify with fresh TUI sessions and generic syntax/test checks.

**Tech Stack:** Markdown ontology artifacts, YAML GitHub Actions workflow, OpenCode v2.0.32 TUI, Python workflow parsers, unittest.

**Spec:** [ONTOLOGY-01](../../../ontology/concept/ontology-asset.md), [EVOLVE-01](../../../ontology/concept/ontology-evolution.md), [SCENE-01](../../../ontology/process/work-scenarios.md), and the OpenCode audit at `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-21-candidate-zero-eight-operation-contract-audit`.

## Global Constraints

- Candidate 0.8.0 stays byte-identical with Git blob `bdbd71525425afee5990ed0dfe0d2bdb71ddf7d3` and SHA-256 `26fbde875f12d0da949140698e95f5739c720eb11b66edf179f9c5518f46a19f`.
- Candidate 0.6.0 and 0.7.0 stay byte-identical with Git blobs `f19bcb8cea1d571b03555d64413c2c81b37d33ce` and `0a4b349d85d52bbb7157ef624a605eee17a9502c`.
- Candidate 0.9.0 remains `status: candidate` and `fixed_by_modeling_act: false`; do not create a formal task, fixed node, implementation, or Verify result.
- Preserve `REQ-SCOPE-001` and `U-PERSISTENCE-SCOPE` as unresolved; do not infer `C-NO-PERSIST` or a scope exclusion.
- `REQ-BC-003` covers only the seeded state-nonmutation requirement; it does not assert that `read()` returns the current value.
- The seed’s increment result sequence remains required, while the API return channel/type remains unknown; `reset()` has no return contract unless the user supplies one.
- `REQ-COMP-001` covers abstract consumption of a legal reading; exact call count, one-to-one freshness, wrapper behavior, and reread policy are not source requirements.
- Keep all existing dirty and untracked work. Do not stage or commit.
- OpenCode artifacts remain under private `/tmp` directories; agent-injected TUI messages are synthetic evidence and do not change H1–H18, CAP-01, or human-origin status.

## Test-First Evidence

- The failing review is the fresh OpenCode v2.0.32 TUI session `ses_ea5b9800dffeVnFuWWbEhNn3FF`, which compared only the specified seed, candidate 0.8.0, and ONTOLOGY-01. Its findings include the unsupported `read()` return contract, `reset() -> integer`, source-overstated one-to-one `legal_count_value` policy, and missing negative-boundary unknown. Preserve its private export under `/tmp/pdca-model-audit-reset-20261021/evidence/`.
- Do not use the aborted scratch-cwd probe `ses_ea5bb22d9ffetTCPZyPIYowUC1` as semantic evidence; it searched stale `/tmp` copies and was stopped.

---

### Task 1: Create the immutable candidate 0.9.0

**Files:**
- Create: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.9.0/model.md`
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

**Interfaces:**
- Consumes: candidate 0.8.0 blob `bdbd71525425afee5990ed0dfe0d2bdb71ddf7d3`; draft seed `tests/host-smoke.md:58-62`; ONTOLOGY-01; fresh audit session `ses_ea5b9800dffeVnFuWWbEhNn3FF`.
- Produces: candidate 0.9.0 with a unique root, exact base blob, complete SHA-256 review reference, corrected requirement statements, and explicit unknowns for `U-OPERATION-RETURN-CONTRACT`, `U-LABEL-READ-MAPPING`, and `U-LABEL-REJECTION-OBSERVABILITY`.

- [x] Copy candidate 0.8.0 to candidate 0.9.0 and change only the new file; set root ID, root path, revision, base ref/blob, interface revision, and digest anchor.
- [x] Make source requirement statements match the draft seed: preserve counter initialization, the increment result sequence from the initial state/upper bound, read nonmutation, reset-to-zero, exact label text, legal-reading consumption, and model-shape requirements without adding operation return claims to those rows.
- [x] Remove `read() -> current value` from `REQ-BC-003` and `C-READ`; retain only the state-preservation predicate and require independent before/after observation under `U-READ-OBSERVABILITY`.
- [x] Remove the `reset() -> integer` declaration and every ambiguous “reset returns 0” statement. Observe reset-to-zero through the next increment result of 1, in conjunction with the seeded increment sequence.
- [x] Replace the generalized increment formula with the exact seeded sequence from initial state; do not require behavior for states or sequences that the seed does not describe.
- [x] Keep `legal_count_value` as an abstract candidate interface for a legal reading. Remove exact one-read-per-label, one-to-one correlation, wrapper, and no-reread clauses from source requirement coverage and node rejection oracles; record those as unconfirmed candidate choices in `U-LABEL-READ-MAPPING`, sourced to the synthetic read-origin review.
- [x] Add `U-OPERATION-RETURN-CONTRACT` for the increment result channel/type interpretation, read result semantics, and reset result; add `U-LABEL-REJECTION-OBSERVABILITY` for whether the negative input boundary can be exposed by a permitted harness.
- [x] Add provenance for lightweight candidate decisions: parameterizing `upper_bound`, modeling aggregate/component endpoints, and the proposed abstract label interface. Remove unsupported UTF-8 wording; keep exact label text semantics.
- [x] Update candidate AC/oracles and unknown references so no read return, reset return, one-to-one call count, or unobservable negative case can be reported as proven.

### Task 2: Align the OpenCode smoke contract with candidate 0.9.0

**Files:**
- Modify: `.github/workflows/opencode-smoke.yml`

**Interfaces:**
- Consumes: candidate 0.9.0 core and NODE-LABEL minimum context from Task 1.
- Produces: fresh-core and child response contracts that distinguish required state/label semantics from unknown return and mapping contracts.

- [x] Change the current candidate input path and generated artifact/context labels from 0.8.0 to 0.9.0; retain historical audit references.
- [x] Update the core JSON prompt/parser to require exact requirement coverage, `read` nonmutation vs unknown return semantics, reset state checked by the next increment result, unresolved label/read mapping policy, and the negative-boundary observability unknown.
- [x] Update the child context/prompt/parser to preserve the legal-reading abstraction and report operation mapping, one-to-one call count, and reread policy as unknown; keep parent/sibling history and counter internals excluded.
- [x] Ensure old 0.8 claims such as `read_invocations_per_label: 1`, `read_return_equals_value_before: true`, and `after_reset_read: 0` are rejected or absent from normalized semantics.
- [x] Preserve exact JSON type checks, identifier allowlists, scope unknowns, fresh-session identity checks, and same-semantics comparison.

### Task 3: Verify candidate 0.9.0 through fresh OpenCode TUI sessions

**Files:**
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

- [x] Run two fresh core TUI sessions and two fresh NODE-LABEL child-context TUI sessions using the updated prompts; each gets a distinct session ID and no write authorization.
- [x] Confirm every answer keeps operation return semantics and detailed read-to-label call policy unknown, keeps `REQ-SCOPE-001` uncovered, and does not claim C-READ conformance without an independent observation surface.
- [x] Run the workflow’s embedded parsers against each response; require both runs in each pair to normalize identically and reject old 0.8-shaped claims.
- [x] Store prompts, pane captures, exports, and parser results under `/tmp/pdca-candidate-09-smoke-20261021/` with directory mode `0700` and file mode `0600`.

### Task 4: Update navigation and close the review

**Files:**
- Modify: `ontology/README.md`
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

- [x] Make candidate 0.9.0 current in ontology navigation and summarize the corrected source/decision boundary; keep candidates 0.6–0.8 historical and unchanged.
- [x] Compute the complete candidate 0.9.0 SHA-256, record it under the model’s digest-ref anchor, then verify the model file did not change afterward.
- [x] Run `python3 -m unittest discover -s tests -v`, `sh -n install.sh`, YAML parsing for every workflow, Skill frontmatter parsing, `git diff --check`, local-link checks, and candidate blob/hash checks.
- [x] Confirm H1–H18 remain `NOT_RUN`, candidate 0.9.0 remains unfixed, no task/implementation/Verify evidence was created, no files are staged, and no commit was made.
