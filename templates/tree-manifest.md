---
schema: pdca.tree-manifest/v1
state: draft
protocol_revision: 3.4.10
work_id: null
tree_revision: null
proposal_id: null
root_node_id: null
tree_spec: null
objects: []
node_bindings: []
knowledge_obligation_refs: []
closure_policy: explicit_required_recursive
view_paths_excluded:
- tree.md
- control/runtime.md
required_scenes:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
---

# 工作目标固定闭包清单草稿

TREE-01唯一签认对象。objects每项固定role、object_id、revision、ref、digest{algorithm:sha256,value:实际摘要}、required与dependencies（object_id列表）；重复ID不同字节拒绝，同字节可去重。role为tree_spec/node/suite/case/fixture/oracle/definition/definition_manifest/protocol_baseline/subject_snapshot/reuse_decision/local_delta/adoption/graph/graph_check/modeling_delivery/modeling_terminal/semantic_review等明确类别。

node_bindings每项含node_id、node_object_id、task_id、attempt、delivery_object_id、terminal_object_id、三个scene的suite_object_ids、seed/role来源与decomposition证据。所有引用必须在objects或其已固定显式分片中可解析，检查图摘要与graph-check输入对应；同节点不同attempt不可拼接。分片覆盖全体，不能只检查顶层摘要。

不包含自身摘要、未来用户响应、消费决策或freeze-receipt，也不包括可变tree.md视图；确认后这些另存单向引用清单。objects.ref必须指向不可变快照或可证明的固定版本；绝不先hash草稿tree.md，再在原路径加frozen字段。每个节点三场景suite语义已定义，真实后续run可not_run；缺case/expected/oracle阻断。未提供真实任务交付/终态时不能以文件齐全替代。

技术readiness引用本清单摘要，放在外部，不回链入objects。subject_snapshot成员按原范围展开；node_bindings.terminal_object_id必须真实解析到独立终态对象，不能只有字符串。graph_check自身绑定graph摘要。每种role至少列出其实际required依赖，不把“可能经某文件引用”当闭包已完成。该模板不能认证真实消息或历史PDCA。

## 用途与容器身份

顶层work/tree/root必须和固定basis、tree_spec一致。node_bindings所引node/delivery/terminal/suite不仅解析成功，还要符合对应role、schema、node、scene及选定task/attempt。交换role或套用其他任务终态不是合法绑定。
