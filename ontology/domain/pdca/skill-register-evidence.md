---
schema: pdca.asset/v1
id: ontology:domain/skill-register-evidence
name: register-evidence
summary: Register evidence for PDCA cycle validation and tracking.
description: Safely register immutable task artifacts with digest and acceptance-criteria mappings. Use before moving Do to Check.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-register-evidence/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


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

## --kind 与本体的锚定（来自 T0414 闭环）

`--kind` 必须命中**允许集合**之一，否则 `register-evidence` 直接报错：

- **`pdca-evidence` 子类型短名**：本体节点 `ontology:entity/evidence-<short>`（其 `relations.specializes` 含 `ontology:concept/pdca-evidence`）提供短名 `<short>`（如 `evidence-convergence-map` → `convergence-map`）。命中时条目写入 `evidence_type_ref` 指向该本体节点 id，使证据锚定到本体（如 `convergence-map`、`review`、`test-result` 等）。
- **支持型 kind（向后兼容）**：`document` / `documentation` / `concept` / `entity` / `process` / `role` / `pattern` / `principle` / `pitfall` / `fact` / `decision` / `knowledge` / `test` / `script` / `adr` / `skill` / `validation-report` / `redirect`。这些作为未定型支持证据被接受，但**不**强制写入 `evidence_type_ref`。

新证据类型请优先定义为 `ontology:entity/evidence-<short>` 节点（specializes `pdca-evidence`），再从 `--kind <short>` 登记，保持证据与本体一致。可用 `scripts/register-evidence.py` 内部的 `evidence_subtype_map()` 查看当前生效的子类型短名集合。
