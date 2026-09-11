---
schema: pdca.ontology-revision/v1.1
state: draft
protocol_revision: 3.4.10
proposal_id: null
candidate_revision: null
origin_task_id: null
origin_work_id: null
origin_node_id: null
library_id: null
definition_id: null
operation: null
base_revision: null
base_digest: null
base_manifest_digest: null
expected_absent: false
proposed_revision: null
payload_ref: null
payload_digest: null
release_manifest_ref: null
release_manifest_digest: null
change_classes: []
change_set: []
compatibility: null
semantic_identity_preserved: null
source_review_refs: []
test_plan_refs: []
reuse_decision_ref: null
impact_ref: null
predecessor_proposal_ref: null
knowledge_obligation_refs: []
reusability_review:
  standalone_semantics: null
  authorized_inputs: null
  case_contracts_ref: null
  private_context_dependencies: []
---

# 共享本体修订候选

EVOLVE-01。wrapper保持candidate（此模板是draft），payload最终字节包括拟发布revision/metadata；没有真实发布回执不能因payload写active就被采用。manifest/payload指向已经存在的固定文件，不指向会被覆盖的最新文件。

## 基准、差异与兼容性

operation=create/revise；create要求expected_absent且无旧base，revise要求完整base三元组。每项change_set含旧/新约束或文字位置、change_class、允许行为是否变化、接口/错误/单位/状态/预期差异、测试与影响。change_classes至少一种，editorial不是默认分类；unknown不得自动迁移。

## 内容审查、正反例与返工

列旧版正例保持项、新版正例/非法行为反例、错误定义控制、case/revision/oracle变化；新约束不能用旧PASS认证。需独立审查最终manifest，并以明确发布权限批准精确对象。审查/批准发生在本记录之后时另存，不回填本记录使其摘要改变。

基准被更早发布改变→保留旧候选与拒绝回执→三方合并并新candidate_revision→全必需回归和独立审查→新授权。Check后或合同改变走新attempt，不能覆盖旧payload。

发布前核验payload能被另一授权工作独立理解与测试；任务日志/确认/actual不移入实体定义。obligation_refs绑定REUSE-01知识义务，候选不等于履行；组合payload若加入新的子版本须重新独立审查和授权。
