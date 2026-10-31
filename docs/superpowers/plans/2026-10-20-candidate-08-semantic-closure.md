# Candidate 0.8 Semantic Closure Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for implementation tasks, with one fresh implementer and scoped review per task. The controller owns final live-session verification. No commit or staging step is authorized.

**Goal:** Create a candidate-0.8.0 successor that covers the omitted modeling-shape requirement, resolves candidate-tree payload identity, and records the source/unknown and observation boundaries found in two independent OpenCode audits.

**Architecture:** Preserve candidate 0.7.0 and 0.6.0 byte-for-byte. Create 0.8.0 as an immutable successor, store its single-file payload SHA-256 in a dated review section referenced by the model root, and update the current OpenCode smoke prompt/parser to consume 0.8.0. Use fresh model sessions and the exact embedded parser as the compatibility seam; keep all raw outputs under private `/tmp` storage.

**Tech Stack:** Markdown ontology assets, YAML GitHub Actions workflow, embedded Python parsers, Bash/ShellCheck, PyYAML, OpenCode v2.0.32.

**Spec:** `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-candidate-0.7-semantic-closure-audit`, interpreted against ONTOLOGY-01, TREE-01, NODE-01, SCENE-01, and DEPENDENCY-01.

## Global Constraints

- Keep candidate 0.6.0 and 0.7.0 byte-identical to their current contents; candidate 0.8.0 remains `status: candidate` and `fixed_by_modeling_act: false`.
- Do not create formal PDCA tasks, attempts, approvals, host receipts, fixed nodes, or Act evidence.
- Preserve “无持久化的示例” as unresolved; do not add `C-NO-PERSIST`, `not_applicable`, or an inferred scope exclusion.
- The bounded-counter seed's line 63 is task-scope; do not project it into domain ontology requirement coverage. Record that classification and its source.
- Keep the existing one-file model-root payload scope. Record its complete SHA-256 outside the hashed model file through the model's stable review-anchor reference.
- Do not add a product-specific semantic validator. Use AI semantic review and mechanical hash/syntax/parser checks only.
- Preserve unrelated dirty worktree files. Do not stage or commit.
- Raw prompts, TUI/CLI JSONL, exports, and responses stay under `/tmp`, in directories mode `0700` and ordinary files mode `0600`.
- Any OpenCode evidence is synthetic Agent evidence. H1–H18, CAP-01, formal Modeling Check/Act, implementation behavior, real Verify, GitHub runner, and pinned OpenCode v1.18.32 remain unverified unless separately evidenced.

---

### Task 1: Create candidate 0.8.0 and update model navigation

**Files:**
- Create: `ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.8.0/model.md`
- Modify: `ontology/README.md`
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

**Interfaces:**
- Consumes: candidate 0.7.0 blob `0a4b349d85d52bbb7157ef624a605eee17a9502c`; the current bounded-counter seed in `tests/host-smoke.md`; the two audit session IDs and findings recorded in the review section.
- Produces: `candidate-0.8.0`, model-shape requirement `REQ-MODEL-SHAPE-001`, observation unknown `U-READ-OBSERVABILITY`, and review anchor `#2026-10-20-candidate-zero-eight-payload-digest` containing the exact SHA-256 of the completed one-file model payload.

- [x] Copy candidate 0.7.0 to candidate 0.8.0, confirm candidate 0.7.0's hash before and after, and update all model-root identity, base, revision, and `legal_count_value` interface revision fields. Set `base_candidate_ref` to candidate 0.7.0 and `base_candidate_blob` to its exact current blob.
- [x] Add `REQ-MODEL-SHAPE-001`: `Counter state and label representation are separately described by inputs, outputs, constraints, and rejectable conditions.` Mark it `covered` and link it to the separate counter/label definitions, constraints, and node acceptance oracles that supply the required structure.
- [x] Change the coverage explanation so it says REQ-SCOPE-001 is the remaining uncovered domain requirement, without implying that other untracked source clauses are resolved by it. In SRC-USER-SEED, identify `tests/host-smoke.md:58-62` as the draft domain seed and state that line 63 is a task-scope boundary governed by host-smoke, not a domain ontology requirement.
- [x] Change the REQ-SCOPE-001 and U-PERSISTENCE-SCOPE descriptions to say “seed phrase” / “source phrase,” leaving its subject and behavioral meaning open.
- [x] Add a `payload_digest_ref` from the model root to `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-candidate-zero-eight-payload-digest`. After the model is final, calculate SHA-256 for the complete single-file payload and record the exact value under that heading without changing the model afterward.
- [x] Expand SRC-PROTOCOL to cite the exact ONTOLOGY-01 and SCENE-01 paths, symbols, asset revisions, repository, and verified baseline commit. Record `tests/host-acceptance.md#H11` and `#H18` for the referenced acceptance unknowns. Update SRC-USER-SEED's limitation to include the draft status.
- [x] Add source and unknown refs to each candidate node per NODE-01. Keep only the existing NODE-LABEL → NODE-COUNTER dependency candidate; explain that NODE-SYSTEM's relation reference describes the composed subtree and does not create a separate direct edge without a distinct fixed interface deliverable.
- [x] Amend C-READ to state that its before/after state signal needs an independent permitted observation surface. Add U-READ-OBSERVABILITY with subject, unresolved question, missing evidence, impact, and resolution condition; do not require private-state access or claim C-READ conformance if the surface is unavailable.
- [x] Update the README to identify candidate 0.8.0 as current, summarize the added requirement and digest evidence, and keep 0.7.0 historical and unchanged.
- [x] Verify candidate 0.6.0 and 0.7.0 hashes, all candidate identity fields, review anchor and SHA-256, source revisions at the pinned commit, requirement IDs, no invented persistence semantics, no `not_applicable`, and `git diff --check`.

### Task 2: Update the OpenCode smoke workflow for candidate 0.8.0

**Files:**
- Modify: `.github/workflows/opencode-smoke.yml`

**Interfaces:**
- Consumes: candidate 0.8.0, `REQ-MODEL-SHAPE-001`, and `U-PERSISTENCE-SCOPE` from Task 1.
- Produces: fresh-core and label-child prompts/parsers whose expected requirement sets and model references match candidate 0.8.0.

- [x] Update only the current candidate references and temporary artifact names from candidate 0.7.0 to 0.8.0; retain historical review references.
- [x] Add a core `covered_requirements` response with the exact seven covered candidate-0.8.0 requirements, including `REQ-MODEL-SHAPE-001`; keep `REQ-SCOPE-001` separate in the unchanged scope contract. Add the model-shape statement to the label-child minimum context and expected requirement set, explicitly limiting it to the in-context label projection.
- [x] Candidate 0.8.0 core uses `NODE-*` acceptance-oracle cross-references. Refine the old blanket token leak check to reject derived-node declarations/projection leakage while permitting only those exact cross-references; keep the ontology core intact and verify an undeclared `NODE-SYSTEM` reference is rejected.
- [x] Preserve strict JSON boolean checks, recursive identifier scanning of dictionary keys and values, nonempty-string limitations, tool boundaries, exclusions, and normalized two-session comparison.
- [x] Extract the exact updated embedded parsers and demonstrate the prior four malformed variants still reject for the intended defects. Use a fresh 0.8-shaped valid response fixture for green parser checks after Task 3 produces it; do not weaken the expected requirements to pass old 0.7 responses.
- [x] Run PyYAML parse, `bash -n` and ShellCheck on all workflow run blocks, Python AST parsing for all heredocs, and `git diff --check`.

### Task 3: Verify candidate 0.8.0 through fresh OpenCode sessions

**Files:**
- Modify: `docs/reviews/2026-10-20-opencode-ai-usefulness.md`

- [x] Run two fresh core and two fresh child OpenCode sessions from the updated workflow prompts using the current local runtime. Require distinct IDs, exact parser success, same normalized semantics per pair, correct scope unknown, correct new requirement, and child tool/exclusion boundaries.
- [x] Save prompts, JSONL, stderr, summaries, parser outputs, and session IDs under `/tmp/pdca-candidate-08-smoke-20261020/` with private permissions; raw replies stay out of the repository.
- [x] Apply the four Task 5 malformed response mutations to the new valid candidate-0.8.0 response pair and verify all reject; verify the unmodified core and child pairs remain green.
- [x] Record version/model/session IDs, exact results, the six confirmed/reasoned 0.7 audit findings and their 0.8 correction, the new payload digest, transient service failures if any, and synthetic evidence limits.
- [x] Recheck candidate 0.6.0 and 0.7.0 unchanged, H1–H18 `NOT_RUN`, no staged files, private artifact modes, and `git diff --check`.
