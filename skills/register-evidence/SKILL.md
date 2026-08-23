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

## 已知坑

- `--file` 必须唯一文件名：同源多证据用 id 前缀（如 ac2-triage-work-SKILL.md），重复文件名会被拒绝（T0266）。
- convergence-map 文本必须与 task.json `meta.convergence` **逐字一致**，否则报 CONVERGENCE_TEXT_MISMATCH；用 `--replace` + 新 id 修正（T0266）。
- `--source` 必须实际存在的文件路径，不存在即失败。
- 同一源文件只能登记**一条**证据：一条证据覆盖多个 AC 用多个 `--criterion` 重复传参，而非拆多条（T0374）。
- **`--source` 是 evidence 目录的唯一写入通道**：勿手动 mkdir/cp 预置同名文件再登记——会撞 duplicate filename；也勿先写空文件占位（空文件会被如实登记 size=0）（T0374）。
- `--replace` supersede 时新条目必须换一个新 `--file` 名，沿用旧名被拒（T0374）。
