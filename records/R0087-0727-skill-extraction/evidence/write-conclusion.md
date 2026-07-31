---
name: write-conclusion
description: Write records/<record-id>/conclusion.md with structured findings, then record verdict in task.json. Use at end of Check phase.
---

Write `records/<record-id>/conclusion.md`:

```markdown
---
schema: pdca.asset/v1
id: <record-id>
phase: check
source_ids: [<evidence-id-1>, ...]
---

## 上下文
## 假设与结果
## 分析
## 失败原因（仅 rejected/partial）
## 适用边界
## 下一轮建议
```

Then record verdict in `task.json` `meta.verdict`:

```json
{
  "outcome": "confirmed|rejected|partial",
  "reason": "<reasoning>",
  "verdict_id": "<unique-id>",
  "at": "<timestamp>"
}
```

Completion criterion: conclusion.md exists and verdict is recorded.