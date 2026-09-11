---
schema: pdca.test-case/v3
case_id: VERIFICATION-P
revision: 1.0.0
node_id: N
scene: ontology_conformance_verification
suite_ref: SUITE-VERIFICATION
constraint_ids:
- R-SHAPE
- R-BINDING
- R-PROVENANCE
ac_ids:
- AC-1
category: positive
required: true
defaults_ref: null
preconditions: 合成数据目录，不访问生产对象
inputs:
  subject_role: formal_record
  fault: none
action: 按固定字段和关系检查；此案例是契约，不是实测结果
expected:
  subject_verdict: pass
forbidden:
- 把无检查当通过
oracle:
  basis: 固定原请求/协议和本案例
observation: 记录字节、位置、判定和范围
failure_signature: 未识别错配或误报合法近邻
cleanup: 保留原始材料
kills: []
regression_issue: null
protocol_revision: 3.4.4
test_layer: structural_record_fixture
subject_ref: null
oracle_ref: null
fault_model: null
injection_invariants: []
source_binding_ref: null
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
