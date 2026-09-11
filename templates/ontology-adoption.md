---
schema: pdca.ontology-adoption/v1
state: draft
protocol_revision: 3.4.10
adoption_id: null
library_id: null
definition_id: null
definition_revision: null
definition_digest: null
manifest_ref: null
manifest_digest: null
binding_kind: null
work_id: null
tree_revision: null
node_id: null
origin_modeling_task_id: null
reuse_decision_ref: null
adopted_constraints: []
excluded_constraints: []
applicability: null
local_delta_ref: null
local_delta_digest: null
effective_contract_ref: null
effective_contract_digest: null
suite_bindings: []
claim_review_refs: []
authorization_scope_ref: null
---

# 不可变知识采用行

REUSE-01定义引用形状，ADOPT-01定义状态/索引。采用行在modeling Do中形成，冻结树/任务基线可引用其摘要；本行不反向引用未来tree清单摘要、Check确认或新scene任务摘要，避免摘要循环。

suite_bindings包含scene、suite/case版本、固定预期来源和适用范围，不包含伪造actual。后续确认accepted、使用任务、affected/cleared等事件另存host索引，不能回填本行改变已冻结摘要。

同一定义可有多个work/tree/node采用行；不能共享任务/Agent或把别处旧PASS写成本任务结果。excluded_constraints每项须说明条件不适用的依据，不得排除适用必需项。
