# T2178 Ontology Conformance Review 1

## Review Basis

- T2178 PRD AC-1 through AC-8
- T2178 `task.json#meta.execution_contract`
- `AGENTS.md` routing and terminology-maintenance rules
- Persisted evidence IDs in the current T2178 evidence manifest

## Result

Status: failed; remain in Do.

The active ontology nodes and `AGENTS.md` pass the submitted scan, but the declared “core authority entrypoint complete set” excludes three current routing/terminology documents that still publish legacy control semantics:

- `README.md`: Do is described as selecting a path by scenario type and contains a `scenario_type` routing table.
- `ontology/README.md`: Plan and Check still apply conditions to `development/bugfix` tasks.
- `pdca/CONTEXT.md`: the shared definition of routing contract remains a scenario-to-path mapping.

`AGENTS.md` explicitly requires terminology changes to be synchronized to `pdca/CONTEXT.md`; therefore these files cannot be omitted from AC-1 or classified as historical/generated material. The current zero-hit claim is incomplete.

## Required Correction

- Add `README.md`, `ontology/README.md`, and `pdca/CONTEXT.md` to the core authority inventory.
- Replace their legacy task routing/classification semantics with the three professional responsibilities and four-field execution contract.
- Preserve ordinary words and historical facts only where they do not define current routing or admission behavior.
- Rerun the complete-set forbidden scan including these files.
- Replace the inventory, change snapshot, validation report, and convergence evidence, retaining exactly one active convergence-map.

The stale deleted-node entry in `ontology/_index/manifest.jsonl` is a pre-existing generated worktree artifact and not an active ontology node; do not overwrite unrelated concurrent index work. Record this boundary explicitly.
