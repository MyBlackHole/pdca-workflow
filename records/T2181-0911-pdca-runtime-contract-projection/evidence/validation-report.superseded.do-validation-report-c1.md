# T2181 Do validation report

This report validates the `ontology_projection` implementation against the T2181
PRD. It is a Do-stage technical report, not a Check verdict, user confirmation,
phase transition, or Act disposition.

## Result

The T2181 implementation satisfies the eleven acceptance criteria within its
authorized scope. Targeted tests, ontology validation, the zero-island check,
skill-index validation, projection verification, residual scanning, compilation,
and `git diff --check` pass. The repository's pre-existing global test and doctor
failures remain and are classified below; no new full-suite failure was introduced.

## Acceptance mapping

| Criterion | Verification | Result |
|---|---|---|
| AC-1 | `runtime-consumer-inventory.md`; `projection-manifest.json` contains authoritative graph, bounded subgraph, and DAG layers; 9/9 actions have ontology/action/criterion links | pass |
| AC-2 | `executable-task.schema.json`, `pdca_runtime.task`, and role/contract negative tests | pass |
| AC-3 | `agent.spawn.required=true`, no fallback; doctor and runtime missing-capability tests | pass |
| AC-4 | content-addressed request plus lock-protected CAS binding; duplicate, concurrent, stale, wrong-task, context-drift, and fresh-context rejection tests | pass |
| AC-5 | receipt fold yields `suspended_waiting_agent`; public CLI has no coordinator execution, wait, or polling command | pass |
| AC-6 | completion/failure/confirmation receipts, artifact and evidence binding, current-task-only recovery bundle, integrity and AC coverage gates | pass |
| AC-7 | old contracts, schemas, resolvers, classifiers, cross-task role scanner, harness, and fixtures removed; residual scan empty | pass |
| AC-8 | research and fix approval are derived only from explicit `required_actions`; report producer exception uses `work_product`; `flow-do` rejects related-task admission | pass |
| AC-9 | all three roles and negative lifecycle boundaries are covered by the targeted runtime suites | pass |
| AC-10 | targeted tests pass; final `tests/` failures are a strict subset of the pre-edit failures; ontology/index/island/projection/diff checks pass | pass with disclosed repository baseline |
| AC-11 | bootstrap request and binding receipt remain separate from runtime receipts; raw SHA-256 values match request/binding; no compatibility parser exists | pass |

## Test results

### T2181 target

Command includes `test_task_contract.py`, `test_ontology_projection_runtime.py`,
`test_pdca_runtime.py`, migrated execution/research/fix/content/harness tests, and
the three doctor capability cases.

Result: `37 passed, 6 subtests passed`.

Additional post-review runtime subset: `18 passed, 6 subtests passed` after receipt
transition validation and context/evidence integrity were tightened.

### Full Python tests directory

Pre-edit observed baseline: `70 failed, 361 passed, 5 skipped, 9 subtests passed`.

Final result: `48 failed, 375 passed, 3 skipped, 15 subtests passed`.

The final 48 failure identities were all present in the pre-edit 70-failure set.
T2181 removed failures tied to the old route/execution controls and introduced no
new full-suite failure. Counts differ from the Plan snapshot because the shared
worktree had already changed before this fresh Agent started; the observed
before/after snapshots are the valid comparison for this execution.

### Repository-wide pytest discovery

Both before and after T2181, repository-wide discovery stops with 7 collection
errors under historical `records/*/evidence`: three missing external demo modules,
one superseded evidence import, and three duplicate-module-name import mismatches.
T2181 did not edit those immutable records.

### Ontology and controls

- `ontology-validate`: pass.
- ontology graph: `nodes: 569`, `edges: 1727`, `islands: 0`.
- skill index: valid, 50 assets.
- T2181 projection verification: 6 authority nodes, 6 bounded nodes, 9 leaves.
- active legacy-control residual scan: zero matches.
- `compileall`: pass.
- `git diff --check`: pass.
- doctor without spawn observation: `agent.spawn=missing`, non-zero as required.
- doctor with spawn observation: `agent.spawn=available`; global result remains
  false solely because existing unrelated seam declarations are missing files.
  T2181's own declared seams are clean.

## Bootstrap audit

- Task raw SHA-256: `b532f0ffbb4634557f77e2eb49cd081bce2c25238531053df41e08c4f31de8b9`.
- PRD raw SHA-256: `995f151571e5e634ec700502143f7dcdb2b5796ac277d5e1ca1a5f1f15761d0c`.
- Bootstrap request raw SHA-256: `5ec555b84e818547b1cba97773070e7fc1cb23299979fa1aa4e41d3dbcdf67aa`.
- Binding Agent: `01a08fa6-ad3a-7800-9102-3dd873b68453`.
- Adapter attestation: `fresh_context=true`, `fork_context=false`, coordinator
  state `suspended_waiting_agent`.

The new runtime accepts only `pdca.agent-dispatch-request/v1` and
`pdca.agent-execution-receipt/v1`; it has no parser for either bootstrap schema.

## Residual limitations

The runtime is intentionally platform-neutral. It validates explicit platform
Adapter observations and receipts but does not implement an Agent API or start
Codex from Python. Filesystem locking uses POSIX `flock`, matching the current
Linux runtime. Global doctor validity and repository-wide pytest discovery remain
red for the unrelated baseline described above.

No Do-to-Check transition, conclusion, user confirmation, verdict, disposition,
journal entry, archive move, or historical record mutation was performed.
