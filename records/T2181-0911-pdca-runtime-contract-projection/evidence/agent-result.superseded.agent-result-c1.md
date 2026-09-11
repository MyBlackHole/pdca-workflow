# T2181 Agent result

## Execution summary

Implemented the platform-neutral PDCA execution core under `pdca_runtime/` and
projected the authority model into a content-addressed T2181 manifest. The runtime
strictly accepts the three ontology responsibilities and the four-field execution
contract, binds one fresh Agent through a lock-protected CAS receipt transaction,
folds execution state from chained receipts, and resumes from current-task
persistence into deterministic ontology conformance review.

Removed the old category/letter route contracts, schemas, resolvers, fixture
harness, prose classifier, and cross-task role scanner. `agent.spawn` is required
with no coordinator fallback. Research and fix approval gates now use explicit
contract actions instead of role inference or an extra task control field.

## Change list

- New core: `pdca_runtime/{errors,io,task,projection,lifecycle,cli}.py` and package API.
- New CLI: `scripts/pdca-runtime.py`.
- New schemas: executable task, context manifest, dispatch request, ontology
  projection manifest, and Agent execution receipt.
- Migrated config/runtime: capability doctor, task schema, `pdca_core.py`,
  `flow_audit.py`, content audit, CI ontology gate, and `flow-do`.
- Removed old route/execution contracts, schemas, resolvers, control harness and
  fixture, category classifier, and cross-task role mismatch scanner.
- Added/migrated tests for all three roles, projection traceability, capability
  rejection, fresh binding, concurrent CAS, receipt states, current-task recovery,
  integrity drift, and removal of old controls.
- Persisted consumer inventory, action bindings, projection/context manifests,
  raw validation outputs, this result, and the detailed validation report in the
  current task directory.

## Verification

- Targeted: `37 passed, 6 subtests passed`.
- Full `tests/`: `48 failed, 375 passed, 3 skipped, 15 subtests passed`; all final
  failures existed in the pre-edit `70 failed` set.
- Repository-wide pytest: unchanged 7 historical evidence collection errors.
- Ontology validation, 0 islands, skill index, T2181 projection, compileall,
  legacy-control residual scan, and diff whitespace checks pass.
- Doctor reports missing spawn as fail-closed; with spawn available, unrelated
  pre-existing seam failures continue to keep global validity false.

## Residual limits and handoff

This implementation does not provide a platform Agent API and does not create a
subprocess Agent. The main session must perform the later current-task conformance
review and Check decision using persisted artifacts and registered evidence.
No user confirmation or verdict has been written, and T2181 remains in Do.
