---
schema: pdca.work-node/v3.4
work_id: null
tree_revision: null
node_id: null
node_revision: null
parent_node_id: null
children: []
definition_refs: []
state: draft
test_suites:
  ontology_modeling: null
  ontology_projection: null
  ontology_conformance_verification: null
protocol_revision: 3.4.10
dependencies: []
resource_scope: []
modeling_decision_ref: null
definition_manifest_refs: []
instance_parameters: {}
local_delta: null
effective_contract_ref: null
effective_contract_digest: null
adoption_refs: []
protocol_baseline_ref: null
subject_snapshot_ref: null
definition_artifact: null
knowledge_obligations: []
decomposition:
  decision: null
  reason: null
  obligation_coverage: []
  independent_parts: []
  workload_basis: null
  context_plan: {}
  budget: null
  progress_measure: null
  child_seeds: []
  composition_checks: []
  stop_conditions: []
  evidence_refs: []
seed_policy: assess_recursively
---

# 目标本体节点草稿

## 实体与范围

实体是什么、职责、允许行为、in_scope/out_of_scope、上层来源及当前出现位置。

## 需求与约束

| requirement/constraint ID | 来源 | 必须性 | 明确规则 | 负责者 | 可观察失败 |
|---|---|---|---|---|---|

## 接口

输入/输出类型、单位、有效范围、前置后置、状态、副作用、错误优先级和版本。

## 组成义务

直接孩子端口/数据控制流映射、组合不变量、故障传播、共享资源所有权。叶必须先按DECOMP-01给出独立理由，再明确无孩子；非叶不得只写“孩子都通过”。

## 交付与上下文预算

固定产物/接口/原始证据位置；必读与按需输入；叶实现/父组合复杂度与拆分终止理由。按 [DECOMP](../ontology/concept/task-decomposition.md#decomp-rejection-witness)将以下内容写入现有decomposition，不另建任务：

| 候选部分或内部步骤 | 独立产物与oracle | 可接受相邻部分但拒收它的情形 | 父组合/错误传播义务 | 预算与上下文依据 |
|---|---|---|---|---|

无独立拒收见证时说明为何保留为内部步骤。已固定真实节点不因本表重新合并。

## 三场景测试

引用已固定的suite，逐约束正例/反例/边界，组合/故障适用项，oracle与变体检测。知识定义可复用，当前节点任务不可省略。

## 实际输入依赖声明

dependencies每项含input_id、producer_node_id/scene/artifact_ref、consumer_node_id/scene、required、source_constraint_ref；无依赖需明确不适用。由DEPENDENCY-01合并场景图，relates_to不生成调度边。resource_scope按RESOURCE-01描述真实对象和副作用。


## 固定定义与局部差异

definition_refs每项必须含library_id/definition_id/revision/content_ref/content_digest/manifest_ref/manifest_digest/binding_kind/applicability/constraint_bindings/excluded_constraints/claim_review_refs/adoption_id。digest使用{algorithm: sha256, value: 实算摘要}；不填latest。完整形状以REUSE-01为准。

local_delta包含scope、base_refs、实例参数、新约束/接口/组合变化、案例增量与compatibility理由；无差异显式写不适用。effective_contract在独立artifacts文件冻结；若当前node本身就是有效契约，不在自身放自己的digest，由tree/交付引用本node摘要（此时effective_contract_ref写self且digest留空并在外部固定）。adoption行同理不回指未来确认摘要。

## 3.4 字段与时点

protocol_baseline_ref固定工作协议闭包，subject_snapshot_ref固定被审对象/输入约定，definition_artifact是业务语义而不是记录路径。definition_refs按REUSE-01；decomposition按DECOMP-01。knowledge_obligations只放固定计划与完成条件，未来publication/终态证据在外部履行记录，不回填本文件。新模板空值只表示草稿，不作为准入或通过。

## definition_artifact填写

kind=reused/local_definition/shared_candidate；semantic_ref/digest固定真正语义，base_definition_refs和candidate_ref按适用性填写。work-node本身就是work_instance，不复制第二主记录。self引用不写自身digest，由固定外层manifest承担。存在性和摘要需实际核验，不用模板占位充当已有定义。
