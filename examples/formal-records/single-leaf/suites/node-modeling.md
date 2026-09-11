---
schema: pdca.test-suite/v3
suite_id: SUITE-MODELING
revision: 1.0.0
node_id: N
scene: ontology_modeling
contract_ref: null
case_refs:
- ref: ../cases/modeling/MODELING-P.md
  digest: 2448ba740f734a7c07e8c600f448234d8c3e4175b89acc1936f47e74e780f4a3
- ref: ../cases/modeling/MODELING-N.md
  digest: 0b9dadfa3f9d3aba9b3f112800dc8af0a3ba12904e4afaeeb676339400af77cf
mutation_refs: []
defaults_ref: null
coverage: []
required_cases:
- MODELING-P
- MODELING-N
repair_budget: null
acceptance_scope: node_scene_artifact
protocol_revision: 3.4.4
test_layer: structural_record_fixture
input_contract: node and actual artifact records
local_binding_refs: []
frozen_contract_suite_ref: null
regression_extension_refs: []
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
