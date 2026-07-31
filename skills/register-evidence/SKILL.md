---
name: register-evidence
description: Safely register immutable task artifacts with digest and acceptance-criteria mappings. Use before moving Do to Check.
---

Use the validated registration command:

```bash
python3 "$PDCA_HOME/scripts/register-evidence.py" \
  --record <record-id> \
  --source <artifact-path> \
  --id <short-id> \
  --kind <type> \
  --criterion <acceptance-criterion-id>
```

The command confines files to `records/<record-id>/evidence/`, computes size and
SHA-256 itself, requires at least one acceptance criterion, rejects duplicate IDs
or filenames, and atomically updates the manifest.

To correct a registered entry, use `--replace <old-id>` (with a new `--id` and a
different `--file`): the old artifact is renamed to `<name>.superseded.<new-id>.ext`
and the old manifest row gains `superseded_by` — never hand-edit the immutable
manifest.

Never hand-write `clarifications.jsonl` entries: use
`python3 "$PDCA_HOME/scripts/append-confirmation.py" --task-dir <task-dir> --source final_confirmation|check_confirmation|direction_confirm --response confirmed --summary "<reason>"`
which stamps the real timestamp and validates the entry before appending.

Completion criterion: every PRD acceptance criterion has trustworthy evidence or
an explicit failure; Do→Check 不接受仅在结论中解释的未覆盖 AC。

After substantive evidence is registered, use `verify-convergence` to create and
register the fixed `convergence-map` control artifact. A convergence map is
excluded from acceptance coverage and cannot count as evidence for itself.
