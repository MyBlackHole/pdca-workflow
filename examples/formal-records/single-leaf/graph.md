---
schema: pdca.dependency-snapshot/v1
work_id: W
tree_revision: TR
graph_revision: G1
scope: all_nodes_all_scenes
parent_graph_ref: null
parent_graph_digest: null
vertices:
- vertex_id: ontology_modeling
  kind: node_scene
  work_id: W
  tree_revision: TR
  node_id: N
  scene: ontology_modeling
- vertex_id: ontology_projection
  kind: node_scene
  work_id: W
  tree_revision: TR
  node_id: N
  scene: ontology_projection
- vertex_id: ontology_conformance_verification
  kind: node_scene
  work_id: W
  tree_revision: TR
  node_id: N
  scene: ontology_conformance_verification
- vertex_id: freeze
  kind: work_event
  work_id: W
  tree_revision: TR
  name: freeze
- vertex_id: release
  kind: work_event
  work_id: W
  tree_revision: TR
  name: release
edges:
- producer: ontology_modeling
  consumer: freeze
  source_constraint_ref: SCENE-01
  required: true
  type: scene_barrier
- producer: freeze
  consumer: ontology_projection
  source_constraint_ref: SCENE-01
  required: true
  type: scene_barrier
- producer: ontology_projection
  consumer: release
  source_constraint_ref: SCENE-01
  required: true
  type: scene_barrier
- producer: release
  consumer: ontology_conformance_verification
  source_constraint_ref: SCENE-01
  required: true
  type: scene_barrier
input_manifest_refs: []
producer_ref: fixture:host
protocol_revision: 3.4.4
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
