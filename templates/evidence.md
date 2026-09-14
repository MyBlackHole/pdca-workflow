---
schema: pdca.evidence/v4
protocol_revision: 4.0.0-rc.2
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

# 主张、实际证据、反证与结论

status区分pass/fail/unknown/not_run/error；默认not_run，不靠输出存在推断执行。工具退出码与对象结果分开，记录实际版本、输入、命令和原始结果。

静态来源不证明动态恢复或性能；unknown不强判二选一。实际结果必须被最终AC汇总消费。
