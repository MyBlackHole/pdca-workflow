---
schema: pdca.tree-spec/v1
state: draft
protocol_revision: 3.4.10
work_id: null
tree_revision: null
proposal_id: null
original_request_ref: null
goal: null
non_goals: []
protocol_baseline_ref: null
subject_snapshot_ref: null
root_node_id: null
nodes: []
role_bindings: []
requirement_ownership: []
knowledge_obligations: []
---

# 不可变工作目标规格草稿

TREE-01的目标对象，不是工作状态视图。节点记录node_id/parent_node_id/children、固定node引用；role_bindings绑定父已确认role/seed与实际孩子，不改变父语义。候选seed递归展开后固定当前闭包，根无父，其余恰好一个组成父。

固定前补齐全部已确认范围和义务；固定后不改state、确认或receipt。禁止出现未来freeze状态/response/control视图指针；本文件摘要仅由外部tree-manifest引用。完整spec不能证明任何Agent已完成，交付/终态在manifest分别核查。

## 核验时点

完整冻结时与外部固定basis核对root/work/tree、必需节点、父子双向关系、根可达性及无环性；node_ref的父子声明也应一致。局部父建模不得套用尚未完成的全树闭包要求。
