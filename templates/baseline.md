---
schema: pdca.baseline/v3.4
task_id: null
baseline_id: null
created_at: null
created_at_source: null
protocol_revision: 3.4.10
work_id: null
tree_revision: null
node_id: null
scene: null
attempt: null
pinned_graph: null
wait_policy_ref: null
capability_requirements: []
resource_scope: []
guarantee_profile: null
modeling_decision_ref: null
definition_refs: []
definition_manifest_refs: []
adoption_refs: []
local_change_intent: null
effective_contract_ref: null
effective_contract_digest: null
protocol_baseline_ref: null
subject_snapshot_ref: null
original_request_ref: null
goal_statement: null
non_goals: []
knowledge_intent: null
decomposition_assessment_plan_ref: null
current_modeling_input_suite_ref: null
produced_node_scene_suite_refs: []
test_binding_ref: null
work_budget_ref: null
work_budget_digest: null
review_run_scope: null
requirements_basis_ref: null
requirements_basis_digest: null
---

# 待确认基线

从当前Plan草稿汇总确认对象，冻结后不覆盖。真实工具计算本文件及快照摘要，摘要由外部引用记录，不在本文件自引用。

## 执行契约

work_product：待填写具体产物及位置。

required_actions：待填写必须动作。

constraints：待填写作用域、安全、资源及必要保证。

testable_signal：待填写观察对象、判断方法、失败判据。

## 固定验收标准

逐项列明AC ID、必须性、预期、验证方法和失败条件。

## 本体版本

列出每个已实际读取节点的ID/revision/摘要和固定版本位置；易变路径需保留任务内快照。

## 执行投影与输入

列出步骤、直接依赖、输入来源及固定版本、产物、失败处理与资源边界。

## 确认摘要

简明说明用户正在确认的目标、实施范围、风险、判定方法与不包含内容。未完成占位项的基线不可请求最终确认。

## 节点测试与返工基线

固定work/tree/node/scene/attempt、suite/case/fixture/oracle、工具绑定、全部必需回归与Do修复预算；未完成占位项不得确认。

## 图、控制与资源

固定已授权pinned_graph/check、派发wait-policy及资源scope/保证等级。预约实例可更新但不得扩大授权范围；冻结基线不使租约永久有效。当前有用的CAP/RESOURCE证据分别引用而不当作用户确认。


## 3.3复用基线

modeling的Plan固定REUSE-01决定、已有定义闭包与本地变更意图，不要求先引用自己尚未生成的最终节点/adoption行；空输出字段明确not_applicable_yet并说明。其他scene固定已形成的definition/adoption/有效契约及全部suite。短时公告view/check是ADOPT运行事实，不把旧检查永久有效化。

## 3.4 字段与时点

protocol_baseline_ref固定工作协议闭包，subject_snapshot_ref固定被审对象/输入约定，definition_artifact是业务语义而不是记录路径。definition_refs按REUSE-01；decomposition按DECOMP-01。knowledge_obligations只放固定计划与完成条件，未来publication/终态证据在外部履行记录，不回填本文件。新模板空值只表示草稿，不作为准入或通过。

current_modeling_input_suite_ref为本次实际验收绑定；produced_node_scene_suite_refs在Plan仅列输出契约/预期位置，不填未来摘要，Do后的真实绑定写delivery，不回填基线。subject_snapshot_ref引用真正逐成员快照。工作预算固定批准的上限/适用scope，实际累计消费另存外部事件。


requirements_basis固定适用权威、原请求/seed与当前要求来源；由核验入口独立选定，不能由候选自证。模板空值是草稿，不代表未知项通过。
