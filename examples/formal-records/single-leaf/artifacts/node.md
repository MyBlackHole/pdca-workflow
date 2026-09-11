---
schema: pdca.work-node/v3.4
work_id: W
tree_revision: TR
node_id: N
node_revision: '1'
parent_node_id: null
children: []
definition_refs: []
state: candidate
test_suites:
  ontology_modeling:
    ref: ../suites/node-modeling.md
    digest: 5451ede14cb85ac2ad38162ab64d3a21fd7d4a32a684675133341b6bc22505c5
  ontology_projection:
    ref: ../suites/node-projection.md
    digest: 2767a507098cdb00dd6fbe15951011cb351299f3ed41d881aed00fa7f66aea2d
  ontology_conformance_verification:
    ref: ../suites/node-verification.md
    digest: 9f10bd4c2556f211da7bf71a72cae9498604033a10f536ec0082f34dc628b156
protocol_revision: 3.4.4
dependencies: []
resource_scope: []
modeling_decision_ref: null
definition_manifest_refs: []
instance_parameters: {}
local_delta: null
effective_contract_ref: self
effective_contract_digest: null
adoption_refs: []
protocol_baseline_ref:
  ref: ../inputs/protocol.md
  digest: 5e2889519440d299afb53ff2bc159c4b8f5c0635ba45408864badfd18c87dc6e
subject_snapshot_ref:
  ref: ../inputs/subject.md
  digest: bcba729e20fdabb1399845aeea812410e1c75c6ff114f93e9e72aadc159898e9
definition_artifact: null
knowledge_obligations: []
decomposition:
  decision: leaf
  reason: 固定单叶示范；未作为真实工作完成
  obligation_coverage:
  - R-SHAPE
  - R-BINDING
  - R-PROVENANCE
  child_seeds: []
seed_policy: assess_recursively
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
