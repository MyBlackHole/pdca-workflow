# AI-Facing Ontology-Driven PDCA Evaluation Plan

> **For agentic workers:** Execute inline in this session. Follow this plan task-by-task and keep each phase gate visible.

**Goal:** Use OpenCode Mini on an isolated RPC workload to measure whether the current PDCA ontology drives AI through modeling, implementation projection, independent verification, and evidence-based workflow improvements.

**Architecture:** Keep a frozen copy of an exact allowlist of PDCA rules and Skills in a disposable fixture. Run a language-agnostic PDCA workflow against the RPC workload with Python 3 as a target-project environment parameter, capture native OpenCode evidence, and compare each transition and artifact against the frozen ontology. Do not change the PDCA rules during the baseline; derive a separate, evidence-backed change plan after the run.

**Tech Stack:** OpenCode Mini in tmux with GPT-6 Luna Max; Git; the repository's existing PDCA Skills and H11 isolation procedure; Python 3 standard library only for the synthetic target workload.

**Spec:** `docs/superpowers/specs/2026-10-23-pdca-implement-ontology-projection-evaluation-design.md`

## Global Constraints

- The PDCA project and ontology remain language-agnostic; Python 3 is only the RPC fixture's target environment.
- Reuse project `opencode-pdca-h11-20261022` and workspace `format-count`, the previously approved identity pair, only inside this new isolated fixture. Let the native PDCA operation generate task/session/event IDs; never invent them.
- Use fixture root `tests/.pdca-ai-ontology-20261023-01/`; keep `pdca-root/`, `target/`, `spec/`, `control/`, `evidence/`, and temporary output separate.
- Never read or write the centralized real `records/`; never copy the whole working tree, provider config, credentials, existing control/evidence, or unrelated untracked files into the fixture.
- Only snapshot the exact source allowlist in Task 2. Record each source path, Git state, and SHA-256, including dirty working-tree versions.
- Keep the operator scenario/oracle outside the Mini's context; do not inject test expectations into the business source or Mini instructions.
- Set every test process's temporary/cache directories inside the fixture. Do not write tests, logs, build outputs, or caches under `/tmp`.
- Keep H11's formatter-only oracle and `NOT_RUN` host-acceptance status unchanged. The RPC integration scenario has a separate ID and verdict.
- Confirm the actual OpenCode Mini runtime model is GPT-6 Luna Max before attributing observations to that model.
- No PDCA ontology, Skill, or baseline scenario edits during live baseline execution. Preserve all failures and unknowns.
- Obtain user confirmation only at the specific identity/source/PDCA phase gates required by the scenario. Do not pre-authorize later phases or fill undecided RPC behavior by inference.

---

### Task 1: Add the separate RPC integration scenario

**Files:**
- Create: `tests/pdca-ai-ontology-evaluation.md`

**Interfaces:**
- Consumes: the approved TCP RPC request in the conversation, the formatter oracle in `tests/h11-live-scenario.md`, and the full-evaluation spec above.
- Produces: a scenario ID `PDCA-AI-RPC-01`, fixed source facts, explicit unknowns, phase evidence requirements, and pass/fail/unknown rules for a multi-node integration scenario.

- [x] **Step 1: Write the scenario contract.**

  Include these approved facts verbatim in substance: custom TCP RPC; a four-byte big-endian length prefix whose value covers the UTF-8 JSON payload bytes; an RPC method that exposes `format_count(n)`; the function accepts non-bool integers 0, 1, and 2 and returns exactly `count=N`, rejects bool/non-integers/out-of-range integers with `ValueError`, and is stateless with no external I/O; Python 3 standard library as the target runtime. State explicitly that these describe the fixture workload, not the PDCA project's implementation language.

- [x] **Step 2: Mark unresolved RPC decisions as unknown.**

  List the request/response JSON envelope, error response, maximum frame size, connection lifetime, concurrency, and timeout behavior as undecided unless a prior user message explicitly fixes a value. Require Model to ask the user or block the affected decision; the scenario must not invent defaults.

- [x] **Step 3: Define the ontology and workflow oracle.**

  Require evidence for source classification, definition/work-instance separation, relation schema/instance separation, constraints, work decomposition, node qualification, composition/dependency, unknown preservation, source→model→artifact mappings, native phase transitions, independent observations, and the four verification chains. Define formatter-only evidence as H11 history, not proof of integration acceptance.

- [x] **Step 4: Check the new scenario document.**

  Run: `git diff --check -- tests/pdca-ai-ontology-evaluation.md`

  Expected: exit 0 with no whitespace errors.

### Task 2: Freeze the exact PDCA source snapshot and create the isolated fixture

**Files:**
- Create: `tests/.pdca-ai-ontology-20261023-01/pdca-root/`
- Create: `tests/.pdca-ai-ontology-20261023-01/pdca-root/.git/`
- Create: `tests/.pdca-ai-ontology-20261023-01/target/`
- Create: `tests/.pdca-ai-ontology-20261023-01/control/`
- Create: `tests/.pdca-ai-ontology-20261023-01/evidence/`
- Create: `tests/.pdca-ai-ontology-20261023-01/tmp/`
- Create: `tests/.pdca-ai-ontology-20261023-01/spec/rpc-service.md`
- Create: `tests/.pdca-ai-ontology-20261023-01/control/source-allowlist.txt`
- Create: `tests/.pdca-ai-ontology-20261023-01/control/source-manifest.tsv`

**Interfaces:**
- Consumes: the exact source allowlist below and the scenario contract from Task 1.
- Produces: a fixture-local PDCA Git root, isolated target Git root, approved source file, and verifiable source manifest.

Allowed PDCA source files:

```text
AGENTS.md
ontology/INDEX.md
ontology/LOAD-MAP.md
ontology/README.md
ontology/concept/capability-protocol.md
ontology/concept/ontology-adoption.md
ontology/concept/ontology-asset.md
ontology/concept/ontology-evolution.md
ontology/concept/ontology-reuse.md
ontology/concept/pdca-ai-friendly-confirmation.md
ontology/concept/pdca-continuous-improvement.md
ontology/concept/pdca-evidence.md
ontology/concept/pdca-execution-contract.md
ontology/concept/pdca-gate.md
ontology/concept/pdca-phase-status.md
ontology/concept/pdca-recovery.md
ontology/concept/pdca-task.md
ontology/concept/pdca-transition.md
ontology/concept/pdca-verdict.md
ontology/concept/resource-ownership.md
ontology/concept/task-control.md
ontology/concept/task-decomposition.md
ontology/concept/task-rework.md
ontology/concept/task-test-case.md
ontology/concept/task-unit-test.md
ontology/concept/work-dependency-graph.md
ontology/concept/work-node-contract.md
ontology/concept/work-ontology-tree.md
ontology/concept/work-tree-scheduling.md
ontology/contracts/agent-dispatch.md
ontology/contracts/entry-recovery.md
ontology/contracts/project-workspace.md
ontology/contracts/record-shapes/agent-assignment.md
ontology/contracts/record-shapes/baseline.md
ontology/contracts/record-shapes/capability-check.md
ontology/contracts/record-shapes/conclusion.md
ontology/contracts/record-shapes/conformance-review.md
ontology/contracts/record-shapes/delivery.md
ontology/contracts/record-shapes/dispatch.md
ontology/contracts/record-shapes/evidence.md
ontology/contracts/record-shapes/index.md
ontology/contracts/record-shapes/ontology-revision.md
ontology/contracts/record-shapes/operation.md
ontology/contracts/record-shapes/project-task-context.md
ontology/contracts/record-shapes/request-decision.md
ontology/contracts/record-shapes/request.md
ontology/contracts/record-shapes/resource-reservation.md
ontology/contracts/record-shapes/response.md
ontology/contracts/record-shapes/task.md
ontology/contracts/record-shapes/transition.md
ontology/process/flow-act.md
ontology/process/flow-check.md
ontology/process/flow-do.md
ontology/process/flow-plan.md
ontology/process/independent-work-review.md
ontology/process/pdca-flow-model.md
ontology/process/select-task-subgraph.md
ontology/process/work-scenarios.md
skills/README.md
skills/pdca/SKILL.md
skills/pdca-assist/SKILL.md
skills/pdca-act/SKILL.md
skills/pdca-check/SKILL.md
skills/pdca-do/SKILL.md
skills/pdca-implement/SKILL.md
skills/pdca-model/SKILL.md
skills/pdca-plan/SKILL.md
skills/pdca-verify/SKILL.md
```

This is a finite copy allowlist, not an instruction to preload all ontology assets. In the fixture, OpenCode must still follow `ontology/LOAD-MAP.md`, the active Skill, and the current scene's dependency-driven read set.

The operator reads these outer-repository documents without copying or injecting them into the Mini context: `tests/h11-live-scenario.md`, `tests/host-acceptance.md`, and `tests/pdca-ai-ontology-evaluation.md`.

- [x] **Step 1: Verify the fixture path is unused.**

  Run: `test ! -e tests/.pdca-ai-ontology-20261023-01`

  Expected: exit 0. If it exists, stop without overwriting it; revise this plan to a reviewed unused fixture path.

- [ ] **Step 2: Copy only the allowlisted source files.**

  Build the fixture `pdca-root/` from the listed files only. Do not copy `.git`, `records/`, `.ignore`, `opencode.json`, provider configuration, credentials, existing H11 control/evidence, or any other working-tree content. Record each copied source's repository-relative path, Git status, and SHA-256 in the source manifest.

- [ ] **Step 3: Freeze the allowlisted PDCA root in a new local Git repository.**

  Run `git init` in fixture `pdca-root/`, add only the allowlisted snapshot, and commit it as the immutable baseline. Verify `git -C tests/.pdca-ai-ontology-20261023-01/pdca-root rev-parse --show-toplevel` resolves to that exact directory and record its commit SHA. This is a new fixture-local Git history; do not copy the source repository's `.git` directory.

- [ ] **Step 4: Create an isolated target Git root.**

  Initialize Git in `target/`, verify its Git top-level resolves to that directory, and ensure it contains no `.pdca/` and no imported product artifacts. Keep target source empty until the separate fixture file `spec/rpc-service.md` is shown to and confirmed by the user.

- [ ] **Step 5: Confirm the test source before formal Model creation.**

  Assemble `spec/rpc-service.md` only from the approved source facts and formatter oracle. Show its exact content and digest to the user before creating the Model task. Record any newly supplied decisions as separate source statements with provenance; preserve all remaining questions as unknown.

- [ ] **Step 6: Verify isolation and snapshot integrity.**

  Resolve both Git roots, compare every fixture source digest with the source manifest, confirm no `records/`, provider config, or credentials were copied, and record the outer repository HEAD plus exact fixture-path status. Stop with `NOT_RUN` if any boundary cannot be verified.

### Task 3: Verify the live OpenCode Mini runtime and binding

**Files:**
- Create: `tests/.pdca-ai-ontology-20261023-01/control/runtime-observation.json`
- Create: `tests/.pdca-ai-ontology-20261023-01/control/binding-observation.json`

**Interfaces:**
- Consumes: fixture roots from Task 2 and the startup procedure in `tests/h11-live-scenario.md`.
- Produces: actual runtime/config/model/tool/source observations and a field-by-field fixture binding comparison.

- [ ] **Step 1: Start a fresh dedicated Mini session using the existing runbook procedure.**

  Record the native OpenCode version, session ID, actual model, loaded instructions and physical Skill Base, declared MCP server count, runtime MCP tool count and schemas. Do not copy provider credentials into the fixture or evidence files.

- [ ] **Step 2: Confirm GPT-6 Luna Max and fixture cwd.**

  Run the runbook shell smoke check and require `pwd` to resolve to `tests/.pdca-ai-ontology-20261023-01/target`. Require the actual model to be GPT-6 Luna Max. If either check fails, preserve the evidence and stop with `NOT_RUN`.

- [ ] **Step 3: Verify binding only after the identity gate.**

  Confirm `project_id=opencode-pdca-h11-20261022`, `workspace_id=format-count`, `records_root` under fixture `pdca-root/records/`, `ontology_root` under fixture `pdca-root/ontology/projects/opencode-pdca-h11-20261022/`, and `target_root` at fixture `target/`. Do not read any binding record before the runbook's identity gate passes.

### Task 4: Run Model and fix a qualified multi-node model

**Files:**
- Create: fixture-local project/workspace/task/attempt records under `tests/.pdca-ai-ontology-20261023-01/pdca-root/records/`
- Create: fixture-local model candidates under `tests/.pdca-ai-ontology-20261023-01/pdca-root/ontology/projects/opencode-pdca-h11-20261022/`
- Create: native Model evidence under `tests/.pdca-ai-ontology-20261023-01/evidence/model/`

**Interfaces:**
- Consumes: approved `spec/rpc-service.md`, frozen PDCA snapshot, and the approved identity pair.
- Produces: a fixed Model revision, source/requirement inventory, decomposed formatter/adapter/service responsibilities where supported, and qualification evidence.

- [ ] **Step 1: Obtain the current root seed confirmation and create exactly one Model task.**

  Use the native PDCA entry and dispatch path. Capture the user-visible seed and approval before creating records. Let the native operation generate the task ID; record the actual return. Do not fabricate IDs or treat dispatch completion as accepted handoff.

- [ ] **Step 2: Run Model Plan→Do→Check→Act in one Agent attempt.**

  Preserve definitions vs work instances, relation schemas vs instances, constraints, provenance, composition/dependency, qualification status, and unknowns. Check source closure and scope before Act. Preserve a failed or blocked attempt as evidence.

- [ ] **Step 3: Stop at unresolved product choices.**

  If request/response shape or any other required runtime behavior is not fixed by approved source, ask the user the specific question and wait. Do not continue to Implement on guessed semantics.

### Task 5: Run Implement against the fixed nodes

**Files:**
- Create: a new fixture-local Implement task/attempt under the same project/workspace records
- Create: target implementation and target tests only inside `tests/.pdca-ai-ontology-20261023-01/target/`
- Create: native Implement evidence under `tests/.pdca-ai-ontology-20261023-01/evidence/implement/`

**Interfaces:**
- Consumes: the fixed Model revision and qualified nodes from Task 4.
- Produces: a release subject with bidirectional source/model/artifact mapping, actual test observations, and Check/Act records.

- [ ] **Step 1: Start a separate Implement task for each qualified node or approved node set.**

  Obtain the current Plan authorization before phase start. Keep assignment task boundaries separate from phase write authorization.

- [ ] **Step 2: Run each Implement task through Plan→Do→Check→Act.**

  Use the frozen mapping and target write scope. Keep red/green test outputs, actual paths, exit codes, source and release digests, and tool failures. If the fixed model is insufficient, stop and report EVOLVE; do not edit the model from Implement.

- [ ] **Step 3: Check mapping and target scope.**

  Verify source→target coverage and target→source justification. Preserve unknown and failure states. Do not treat green tests or completion messages as independent Verify.

### Task 6: Run an independent Verify and terminalize each task

**Files:**
- Create: a fresh-Agent Verify task/attempt under the same fixture project/workspace
- Create: native Verify evidence under `tests/.pdca-ai-ontology-20261023-01/evidence/verify/`
- Create: a sanitized summary at `docs/reviews/2026-10-23-pdca-ai-ontology-evaluation.md`

**Interfaces:**
- Consumes: immutable Model revision, Implement release digest, fixed source/oracles, and mapping evidence.
- Produces: independent behavior observations, four-chain conclusions, per-subject verdicts, and a traceable evaluation report.

- [ ] **Step 1: Start Verify with a fresh Agent and independent read scope.**

  Freeze the exact source/model/node/mapping/release/oracle digests in Verify Plan. The Verify Agent must not write the release target.

- [ ] **Step 2: Run Verify Plan→Do→Check→Act.**

  Independently execute fixed positive and negative cases, inspect composition/dependency, and report requirement→model, model→implementation, implementation→behavior, and composition/dependency conclusions. Keep mutant/control observations separate from release verdicts.

- [ ] **Step 3: Write the sanitized evaluation report.**

  Separate task execution, subject conformance, scene coverage, and delivery usability. Attribute each finding to ontology, Skill projection, phase/gate, host/configuration, operator/test design, or provider transport with native evidence references. Keep H11 and H1–H18 statuses unchanged unless their own acceptance rules are separately satisfied.

### Task 7: Compare mature Skill practices after the baseline

**Files:**
- Create: `docs/reviews/2026-10-23-pdca-skill-practice-comparison.md`

**Interfaces:**
- Consumes: the evaluation report, the repository's current TDD/debugging/verification Skills, and the pinned public sources `https://github.com/anthropics/skills` and `https://github.com/obra/superpowers-skills`.
- Produces: a source-attributed comparison of specific practices and their fit with the PDCA ontology; this task does not modify PDCA rules.

- [ ] **Step 1: Pin the reviewed source versions.**

  Record repository URL, branch/tag, commit SHA, retrieval date, and the exact Skill files reviewed for both repositories. Do not rely on search summaries or unpinned `main` content in the comparison.

- [ ] **Step 2: Compare concrete workflow practices.**

  Compare how each selected Skill defines entry conditions, actions, evidence, failure recovery, and completion. Map each useful practice to an existing PDCA ontology concept or record the missing ontology link; do not treat similar wording as semantic equivalence. Use these installed local references for the current baseline: `skills/tdd-workflow/SKILL.md`, `skills/systematic-debugging/SKILL.md`, and `/home/black/.codex/plugins/cache/openai-api-curated/superpowers/0722921d/skills/verification-before-completion/SKILL.md`.

- [ ] **Step 3: Record fit and limits.**

  For each candidate practice, state its source, the PDCA object/gate it could strengthen, the observed baseline issue it addresses, and any conflict or duplication. Exclude practices without an evidence-backed PDCA mapping.

### Task 8: Prepare and execute the evidence-backed optimization plan

**Files:**
- Create: `docs/superpowers/plans/2026-10-23-pdca-ai-ontology-improvements.md`

**Interfaces:**
- Consumes: the Task 6 evaluation report and Task 7 comparison.
- Produces: a minimal modification plan for ontology/Skills, plus a regression oracle for each accepted finding.

- [ ] **Step 1: Classify only findings backed by native behavior evidence.**

  Exclude unverified guesses and provider/host failures from ontology fixes. Cite the exact requirement, ontology source, Skill projection, observed action, and expected corrected behavior.

- [ ] **Step 2: Define a regression for each proposed rule change.**

  Include one normal case and one counterexample for the behavior being corrected. Keep the baseline fixture immutable and run corrections using a new frozen snapshot and fresh Mini session.

- [ ] **Step 3: Self-review and commit the focused improvement plan.**

  Run `git diff --check -- docs/superpowers/plans/2026-10-23-pdca-ai-ontology-improvements.md`; commit only that plan file. Implement the selected changes inline under the user's existing optimization authorization, and verify them against the plan's regression oracle.

## Self-Review Checklist

- Scenario boundaries: H11 remains formatter-only; multi-node RPC uses a distinct scenario and verdict.
- Language separation: Python applies to target fixture only; ontology and PDCA process remain language-agnostic.
- Source integrity: unresolved RPC behavior stays unknown until the user fixes it; reports never become original source.
- Isolation: only exact allowlisted rules enter the fixture; records, secrets, OpenCode config, and prior control evidence stay out.
- Full flow: Model, each Implement task, and independent Verify each have their own Plan→Do→Check→Act evidence.
- Validity: green tests, final messages, dispatch return codes, or Mini self-reports never replace native receipts and independent observations.
- Scope: changes to PDCA rules happen only after a baseline report and a separate focused plan.
- Skill comparison: public Skill repositories are version-pinned and provide technique candidates; the PDCA ontology remains the authority for process semantics.
