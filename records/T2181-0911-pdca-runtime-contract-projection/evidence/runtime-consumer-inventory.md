# T2181 runtime consumer inventory

Scope is limited to active runtime surfaces: `config/`, `schemas/`, `scripts/`,
`tests/`, top-level `pdca/*.json`, the authority ontology assets named by the
bootstrap request, and this task directory. Historical records, journals,
archived tasks, and unrelated active tasks are excluded.

## Pre-migration consumers

| Surface | Legacy consumer | Disposition |
|---|---|---|
| config | `config/capabilities.yaml` made `agent.spawn` optional and declared a coordinator fallback | spawn is required; fallback removed |
| machine contract | `pdca/ai-friendliness-route-contract.json` encoded six categories and letter routes | deleted |
| machine contract | `pdca/ai-execution-contract.json` encoded category-specific test/fix paths | deleted |
| schema | `schemas/ai-friendliness-route-contract.schema.json` and `schemas/ai-execution-contract.schema.json` fixed the old route tables | deleted |
| schema | `schemas/task.schema.json` allowed `requires_fix_confirmation` outside the four-field contract | property removed; executable boundary added |
| Python | both `resolve-ai-*.py` resolvers selected a route by category | deleted |
| Python | `run-ai-friendliness-fixtures.py` drove the old resolver contracts | deleted |
| Python | `scenario-boundary-check.py` inferred execution behavior from prose | deleted |
| Python | `check-scenario-mismatch.py` scanned related task state for role control | deleted; CI call removed |
| Python | `pdca_core.py` inferred research from ontology role | changed to explicit `required_actions`; report producers are not self-blocked |
| Python | `flow_audit.py` consumed `requires_fix_confirmation` | changed to an explicit required action |
| tests | route/execution resolver suites and category fixtures asserted old control behavior | removed or rewritten against `pdca_runtime` |
| ontology | `flow-do` allowed an archived related task report to satisfy admission | current-task evidence only |

## Post-migration authority

- Professional responsibility is exactly one of `ontology_modeling`,
  `ontology_projection`, or `ontology_conformance_verification`.
- Work is described only by `work_product`, `required_actions`, `constraints`,
  and `testable_signal`.
- `pdca_runtime/` owns projection, dispatch binding, receipt state, and recovery.
- Platform code owns creation of a fresh native Agent and attests that fact in
  a binding receipt; Python never starts an Agent process.
- Recovery follows only paths persisted by the current task and never follows
  task relationship fields.
