---
name: register-evidence
description: Copy task artifacts into records/<record-id>/evidence/ and append to manifest.jsonl. Use when completing a Do or Check step that produces artifacts.
---

Copy key artifacts from the task workspace to the immutable record location:

```bash
mkdir -p records/<record-id>/evidence/
cp <artifact-path> records/<record-id>/evidence/
```

Append each artifact to `evidence/manifest.jsonl`:

```
{"id": "<short-id>", "file": "<filename>", "kind": "<type>", "size": <bytes>, "digest": "<sha256>", "at": "<timestamp>"}
```

Completion criterion: all planned artifacts are registered in manifest.