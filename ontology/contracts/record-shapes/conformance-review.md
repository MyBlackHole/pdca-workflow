---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# Verify scene conformance matrix：记录格式

本契约只保存 `pdca-verify` scene 的结构化 requirement/model/implementation/behavior 核验矩阵。
它不是当前 task 的 Check conclusion，也不替代 EVIDENCE-01 / VERDICT-01。

## 示例

```markdown
---
schema: pdca.conformance-review/v4
protocol_revision: 4.0.0-rc.4
task_id: null
attempt: null
requirement_refs: []
definition_refs: []
subject_refs: []
projection_map_ref: null
findings: []
result: not_run
---

# Verify scene conformance matrix

`findings` 可记录：

- requirement -> model 的覆盖/缺口；
- model -> implementation 的 mapping/无依据增加；
- implementation -> behavior 的实际 observation；
- 必要 composition/dependency interface 一致性。

每个 finding 保留 subject、requirement/definition/target、observation/evidence refs、counterevidence 与 limitation。
`result` 只是这个 scene matrix 的局部 summary claim；Verify task 的正式 Check verdict 仍由 conclusion/VERDICT-01 聚合。

哈希、链接、文件数量、独立 Agent 身份或 reviewer 共识都不能替代 observation/evidence。
```
