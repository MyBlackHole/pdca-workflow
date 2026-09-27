---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# Check verdict aggregate：记录格式

本契约只保存 VERDICT-01 对当前 Check subject 的聚合结果。
它不执行 test/review，不生成 evidence，也不产生下一阶段授权。

## 示例

```markdown
---
schema: pdca.conclusion/v4
protocol_revision: 4.0.0-rc.5
task_id: null
attempt: null
run_id: null
subject_refs: []
acceptance_results: []
subject_conformance: unknown
evidence_refs: []
counter_evidence_refs: []
recommendation: null
limitations: []
---

# Check verdict aggregate

`acceptance_results` 逐 AC 引用 EVIDENCE-01 的 pass/fail/unknown/not_run；
`subject_conformance` 只按 VERDICT-01 聚合当前固定 subject 的必需 evidence。
多数 PASS 不能覆盖必需 fail/unknown/not_run。

`recommendation` 只是后续 Act/Do 的候选处置说明，不是用户授权，也不能改写 actual/oracle/conformance。
task_execution、delivery_usable、scene coverage 如需汇总，由 delivery record 引用真实 conclusion/Act/scene facts，
不要在 conclusion 里凭建议推断。
```
