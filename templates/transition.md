---
schema: pdca.transition-receipt/v3.2
task_id: null
sequence: null
from: null
to: null
previous_receipt_digest: null
baseline_digest: null
gate_id: null
inputs: []
confirmation_refs: []
test_run_refs: []
result_package_refs: []
decision: null
actor_ref: null
recorded_at: null
protocol_revision: 3.4.11
attempt: null
inputs_digest: null
confirmation_decision_refs: []
writer_grant_ref: null
observed_control_revision: null
commit_receipt_ref: null
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref: null
gate_check_ref: null
gate_check_digest: null
---

# 单阶段转换回执

from/to/gate_id必须来自实际合法transition节点。记录真实输入ref与digest，decision必须来自门禁事实，不预填approved。

## 门禁核验

逐项记录满足依据或失败。任何必需条件不成立就不生成生效回执；失败检查可作为独立诊断记录，不冒充转换。

## 完整性

本回执摘要由后续快照/回执引用，不自引用。完整写入并重读核对后才能更新task.md。写入中断、链分叉、未知副作用按RECOVERY-01处理。

固定sequence为1 plan→do、2 do→check、3 check→act、4 act→archive。唯一键(task_id,sequence)，相同键内容冲突必须阻断；control事件不占编号，operation_id独立。commit_receipt_ref如不可获得应声明保证不足，不能伪填。
