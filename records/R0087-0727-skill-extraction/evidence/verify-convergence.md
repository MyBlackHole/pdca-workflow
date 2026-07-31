---
name: verify-convergence
description: Check that all required evidence listed in task.json meta.convergence are present in evidence/manifest.jsonl. Use before writing conclusion.
---

1. Read `task.json` `meta.convergence` — the list of required evidence IDs.
2. Read `records/<record-id>/evidence/manifest.jsonl` — the actual entries.
3. For each required ID:
   - Found → skip
   - Missing → report to user and ask to supply
4. Report overall status: all satisfied or gaps remain.

Completion criterion: all required evidence confirmed present, or gaps reported.