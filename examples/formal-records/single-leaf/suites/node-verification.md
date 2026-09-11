---
schema: pdca.test-suite/v3
suite_id: SUITE-VERIFICATION
revision: 1.0.0
node_id: N
scene: ontology_conformance_verification
contract_ref: null
case_refs:
- ref: ../cases/verification/VERIFICATION-P.md
  digest: 92f5d01900256e89afd9d8f0caa7d5830ccbb5cb1f8be0bafb9cff0584a5e54e
- ref: ../cases/verification/VERIFICATION-N.md
  digest: 10216607d495ccd9085409e17b57d4c7c81b284ac7add58e20acffdb2de4f709
mutation_refs: []
defaults_ref: null
coverage: []
required_cases:
- VERIFICATION-P
- VERIFICATION-N
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
