---
schema: pdca.work-tree/v3
example_only: true
execution_status: NOT_RUN
work_id: EXAMPLE-BOUNDED-WRITE
tree_revision: tree-2
root_node_id: R
state: example
nodes:
- node_id: R
  parent_node_id: null
  children:
  - A
  - B
  node_ref: nodes/R.md
- node_id: A
  parent_node_id: R
  children:
  - A1
  - A2
  node_ref: nodes/A.md
- node_id: A1
  parent_node_id: A
  children: []
  node_ref: nodes/A1.md
- node_id: A2
  parent_node_id: A
  children: []
  node_ref: nodes/A2.md
- node_id: B
  parent_node_id: R
  children:
  - B1
  - B2
  node_ref: nodes/B.md
- node_id: B1
  parent_node_id: B
  children: []
  node_ref: ../range-task/node.md
- node_id: B2
  parent_node_id: B
  children: []
  node_ref: nodes/B2.md
---


# 七节点组成树

R由A/B组成；A由A1/A2组成；B由B1/B2组成。每个节点三个场景各有独立完整PDCA，首次基准21任务；失败/修复增加attempt，不删除历史。

这里的example状态不是已冻结用户目标，不提供伪造摘要或用户确认。真实工作须按TREE-01生成和冻结。
