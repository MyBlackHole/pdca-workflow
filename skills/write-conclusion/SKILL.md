---
name: write-conclusion
description: Write records/<record-id>/conclusion.md with structured findings, then record verdict in task.json. Use at end of Check phase.
---

Write `$PDCA_HOME/records/<record-id>/conclusion.md`:

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

## 已知坑

- conclusion.md 必须给出 verdict（verdict_id/outcome/reason/at 四字段）与逐条 AC 判定；缺 verdict 或含糊判定会导致 Check 无法通过（T0265）。
- 结论中不得仅解释未覆盖的 AC——每个 AC 须有证据或显式失败。
