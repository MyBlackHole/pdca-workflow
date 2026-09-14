---
schema: pdca.conclusion/v4
protocol_revision: 4.0.0-rc.2
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

# Check结论，等待用户决定

逐AC列pass/fail/unknown/not_run和来源，区分确定违例、未验证及建议。检查成功不代表对象成功；缺本体源／映射不能用多数PASS遮盖。

推荐接受、Do返修、延期或Act仅归档；未收到对应阶段启动操作不执行。用户认可不改写actual和oracle。
