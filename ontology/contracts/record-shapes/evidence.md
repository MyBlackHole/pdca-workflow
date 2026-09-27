---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# Claim evidence binding：记录格式

本契约只保存 EVIDENCE-01 的**局部 claim ↔ observation** 事实。
它不定义 case、不执行 test，也不代表整个 task 的最终 verdict。

## 示例

```markdown
---
schema: pdca.evidence/v4
protocol_revision: 4.0.0-rc.3
task_id: null
attempt: null
run_id: null
subject_refs: []
claim: null
acceptance_ref: null
expected: null
actual: null
tool_ref: null
raw_result_refs: []
counter_evidence: []
status: not_run
limitations: []
---

# Claim evidence binding

`status=pass/fail/unknown/not_run/error` 只表示当前固定 subject 上这条 claim/AC 的局部 evidence 状态。
expected/oracle 必须可追溯到 Plan/CASE；actual 必须来自真实 observation/source。

tool/command 成功与 subject conformance 分开；reviewer finding 也只是 claim，必须有 observation/raw refs 才能升级 evidence。
当前 subject 变化后旧 evidence 保留历史，不自动用于新版本。

整个 Check/task 的 subject_conformance 与其他 verdict 维度只写 conclusion/VERDICT-01。
```
