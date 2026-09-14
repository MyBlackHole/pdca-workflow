---
schema: pdca.delivery/v3.4
task_id: null
work_id: null
tree_revision: null
node_id: null
scene: null
attempt: null
suite_ref: null
artifact_refs: []
child_delivery_refs: []
test_run_refs: []
task_verdict: null
delivery_usable: null
limitations: []
open_issues: []
node_local_pass: null
delivery_profile: full
protocol_revision: 3.4.11
definition_refs: []
definition_manifest_refs: []
modeling_decision_ref: null
adoption_refs: []
effective_contract_ref: null
effective_contract_digest: null
shared_candidate_refs: []
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
current_modeling_input_suite_ref: null
produced_node_scene_suite_refs: []
issue_impact_refs: []
---

# 节点固定交付包

先固定真实对象再生成清单，外部索引引用清单摘要。明确输入/产物/孩子/套件版本、全必需测试结果及失败限制；任务completed不自动意味着delivery_usable。

## 接口和真实产物

具名位置、实际digest、输入输出/错误/状态契约；非叶列真实组合证据，不以stub作最终交付。

## 结果与后续

为什么可用/不可用；列实际已验证范围、明确违例、证据不足/未运行、延期事项及原因，沿用原TEST/VERDICT值，不增加best-effort等成功状态。未满足的必需义务不能用“延期”消除。局部执行成功与独立审查/最终发布分开；修复后旧包保留并按依赖标stale，不覆盖。


## 局部通过与可用性

node_local_pass仅代表本节点/场景全部必需验收。delivery_profile固定full；delivery_usable须由宿主结合本包与独立终态回执核对。open_issues可包含待祖先回归/独立审查的工作缺陷，不因此反向阻止本地交付；本节点未决副作用/必需失败则阻断。父需另核输入契约。


## 知识采用与候选

definition_refs采用REUSE-01列表，旧definition_ref单值不自动迁移。modeling交付自己的NODE/采用/局部差异；shared_candidate_refs只是待发布对象，不替代当前目标和验收。候选未发布不阻塞已独立满足的本地交付；发布须EVOLVE-01真实独立审查/授权/提交。后续scope/task/confirm/run另建，不共享旧回执。

## 3.4 字段与时点

protocol_baseline_ref固定工作协议闭包，subject_snapshot_ref固定被审对象/输入约定，definition_artifact是业务语义而不是记录路径。definition_refs按REUSE-01；decomposition按DECOMP-01。knowledge_obligations只放固定计划与完成条件，未来publication/终态证据在外部履行记录，不回填本文件。新模板空值只表示草稿，不作为准入或通过。

本包definition_artifact引用已存在定义/有效契约，knowledge_obligations只引用固定计划；实际publication履行和任务终态在包外事件中关联，不能回写此包。三个scene的套件规范完整不代表未来场景实际运行。


## 结果消费核对

核对交付对象与已审查包为同一有效版本；未核验的新内容不继承旧结论。审查报告交付可包含对象fail，但实现交付不能借用审查任务成功冒充对象通过。
