---
schema: pdca.recursive-hierarchy-fixture/v1
fixture_only: true
runtime_result: NOT_RUN
root_node_id: R
nodes:
- node_id: R
  parent_node_id: null
  children:
  - N
  - S
  - F
  - T
  - U
  business_definition: ontology:concept/audit/project-review
  definition_ref: ../../ontology/concept/audit/project-review.md
  scope: 全局汇聚与跨分片
  seed_policy: assess_recursively
  illustrated_assessment: composite
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/project-review/suite.md
  runtime_tasks: []
- node_id: N
  parent_node_id: R
  children: []
  business_definition: ontology:concept/audit/rule-consistency-review
  definition_ref: ../../ontology/concept/audit/rule-consistency-review.md
  scope: 协议运行规则
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/rule-consistency-review/suite.md
  runtime_tasks: []
- node_id: S
  parent_node_id: R
  children: []
  business_definition: ontology:concept/audit/rule-consistency-review
  definition_ref: ../../ontology/concept/audit/rule-consistency-review.md
  scope: 结构/类型/唯一权威
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/rule-consistency-review/suite.md
  runtime_tasks: []
- node_id: F
  parent_node_id: R
  children:
  - F_A
  - F_B
  business_definition: ontology:concept/audit/source-claim-review
  definition_ref: ../../ontology/concept/audit/source-claim-review.md
  scope: 资料事实组合
  seed_policy: assess_recursively
  illustrated_assessment: composite
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/source-claim-review/suite.md
  runtime_tasks: []
- node_id: T
  parent_node_id: R
  children: []
  business_definition: ontology:concept/audit/test-contract-review
  definition_ref: ../../ontology/concept/audit/test-contract-review.md
  scope: 案例/oracle/返工
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/test-contract-review/suite.md
  runtime_tasks: []
- node_id: U
  parent_node_id: R
  children: []
  business_definition: ontology:concept/audit/rule-consistency-review
  definition_ref: ../../ontology/concept/audit/rule-consistency-review.md
  scope: 复用/发布/采用
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/rule-consistency-review/suite.md
  runtime_tasks: []
- node_id: F_A
  parent_node_id: F
  children: []
  business_definition: ontology:concept/audit/source-claim-review
  definition_ref: ../../ontology/concept/audit/source-claim-review.md
  scope: 合成领域A固定版本主张
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/source-claim-review/suite.md
  runtime_tasks: []
- node_id: F_B
  parent_node_id: F
  children: []
  business_definition: ontology:concept/audit/source-claim-review
  definition_ref: ../../ontology/concept/audit/source-claim-review.md
  scope: 合成领域B固定版本主张
  seed_policy: assess_recursively
  illustrated_assessment: leaf_subject_to_actual_evidence
  required_scenes:
  - ontology_modeling
  - ontology_projection
  - ontology_conformance_verification
  test_contract_ref: ../../tests/audit-contracts/source-claim-review/suite.md
  runtime_tasks: []
---

# 八节点示意：孩子再次判断并拆出子本体

这是教学目标关系，不是新的用户工作记录，也没有声明任何节点已通过叶子评估或完整PDCA。R的事实角色F继续拆成F_A/F_B；每个节点映射已有业务定义而不是复制一份同义共享本体。N/S/U不同实例采用相同规则审查定义，知识共享不造成第二父。

真正使用时逐节点按DECOMP评估工作量和必要上下文，再确认最终拓扑；不能复制本例“叶子”标签作为证据。实际任务按最终N逐scene覆盖，首次无返工覆盖为3N，示例没有预填24个成功任务或Agent。该图只验证组成结构与角色覆盖，不是端到端宿主试点。

F_A/F_B仅代表合成资料范围，不是对密码/文件系统领域知识已完成审查。当前实例参数、固定对象和工具绑定应在真实任务中补齐；suite语义可复用，run不可复用。
