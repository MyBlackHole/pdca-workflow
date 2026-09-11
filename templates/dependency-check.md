---
schema: pdca.dependency-check/v1
check_id: null
work_id: null
tree_revision: null
graph_ref: null
graph_revision: null
graph_digest: null
expected_parent_ref: null
expected_parent_digest: null
checkpoint: null
algorithm: null
checker_ref: null
vertices_checked: null
edges_checked: null
result: null
cycle_witness: []
topological_order_ref: null
source_edge_refs: []
commit_receipt_ref: null
protocol_revision: 3.4.10
---

# 依赖图检查与提交回执草稿

DEPENDENCY-01要求candidate_edge_change/tree_freeze/plan_input_binding/dispatch/plan_to_do校验相同授权图版本；算法DFS三色或Kahn加环路径。通过需完整邻接图检查，不是仅找双向边。

## 结果与提交

result=acyclic/cyclic/invalid/unknown。cyclic保存一条真实闭合路径及边来源；Kahn剩余集合不等于单一环。提交核对expected_parent和当前授权scope，图变动不复用旧PASS。空知识图通过不能代替此工作实例图。
