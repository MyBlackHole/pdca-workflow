---
schema: pdca.asset/v1
id: ontology:domain/skill-write-conclusion
name: write-conclusion
summary: Write conclusions for PDCA cycles with proper evidence and dispositions.
description: Write records/<record-id>/conclusion.md with structured findings, then record verdict in task.json. Use at end of Check phase.
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
---

--
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

"分析"节逐条 AC 判定行使用固定格式（保证机器可检索）：

```markdown
- **AC-1** ✅ <一句话判定>（<evidence-id>）
- **AC-2** ❌ <未满足原因>（<evidence-id 或 explicit-failure 说明>）
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

Completion criterion: conclusion.md 含 verdict 四字段（outcome/reason/verdict_id/at）且**每个 AC** 都有一行 `✅/❌` 判定指向证据 ID；缺任一字段或任一 AC 无判定行即未完成。research 场景的关键结论还须附可复核验证途径（与 skills/research 第 4 步呼应）。

## 已知坑

- 判据已前置化：四字段与逐条判定是完成条件本身，不再是事后补救——写完即自检，勿依赖 Check 门禁兜底（T0265 源头，T0376 固化）。
- 结论中不得仅解释未覆盖的 AC——每个 AC 须有证据或显式失败。
