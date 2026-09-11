---
schema: pdca.reuse-decision/v1.1
state: draft
protocol_revision: 3.4.10
decision_id: null
task_id: null
work_id: null
tree_revision: null
node_id: null
scene: ontology_modeling
attempt: null
search_scope: []
queries: []
searched_catalog_refs: []
candidates: []
coverage_limitations: []
decision: null
selected_definition_refs: []
instance_parameters: {}
local_change_intent: null
requirement_mapping: []
not_selected: []
change_intent: null
instance_action: create_occurrence
protocol_baseline_ref: null
subject_snapshot_ref: null
knowledge_disposition: null
knowledge_obligations: []
definition_artifact_plan: null
decomposition_plan_ref: null
---

# 建模复用决定草稿

权威REUSE-01；Plan检索和决定，不是已经生成或批准的本体。来源用户/父seed需具名引用。queries记录实际查询，candidates含版本、相似点、不适用点、证据与排除理由；搜索不可达不等于没有已有定义。

## 决定及依据

reuse/local_extension/revise_shared/create四选一。说明已有定义是否适用，为什么不是其他方式；create附没有适用候选的实际范围，revise_shared附共享价值与计划变更，不指向尚未生成的未来payload。

## 要求覆盖

每项requirement_mapping包含parent_requirement_ref、source_constraint_refs、coverage（covered/local_needed/conflict/unknown）、适用范围、必须性和拟用测试。conflict/unknown影响必需要求则不能进入Do。

## 固定定义元素

selected_definition_refs每项形状同NODE definition_refs（REUSE-01），含library_id、definition_id、revision、content_ref/digest、manifest_ref/digest、binding_kind、applicability、constraint_bindings、excluded_constraints、claim_review_refs和adoption_id（可先分配身份，最终行由Do产出，不提前引用未来行摘要）。期望与决定必须在运行前固定，结果记录到独立交付。

## 局部差异或共享意图

local_change_intent写本次参数/约束/接口/组合的计划边界；最终delta另存在NODE产物中。共享意图不自动获得发布权限，证据/独立审查/真实授权按EVOLVE-01。

## 入库义务（REUSE-01）

knowledge_disposition=existing_reuse/local_only/shared_required/shared_deferred；knowledge_obligations每项至少obligation_id、scope、required、target_library_id、target_definition_id、fulfillment_mode（adopt_existing/publish_new/publish_revision）、owner_work_node_ref、completion_criteria、authorization_basis、defer_reason/continuation（适用时）。来源不可达不等于没有候选；本地参数不自动修改共享定义。计划不引用未来发布回执摘要，实际履行另存。共享必需项未发布可以本地candidate_only结束，但工作知识目标仍未满足。

实例新建与知识create独立决定。selected_definition_refs应是可用业务语义；全是流程规范时需另说明本节点业务定义在哪里。
