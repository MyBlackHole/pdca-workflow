---
work_id: W
tree_revision: TR
objects:
- object_id: graphcheck
  role: graph_check
  required: true
  ref: graphcheck.md
  digest: 7271bfa38efc281e9dba99c6db2014d9126ebf48e33df598d75ea941625f1666
- object_id: graph
  role: graph
  required: true
  ref: graph.md
  digest: 692921240787cc1ea9f7333c3dab8deebfe41c23f0472d338088363debe1c525
- object_id: terminal
  role: modeling_terminal
  required: true
  ref: terminal.md
  digest: 5e4506847fbaf38c6ea506cc259d7e5fd8d42eb85dd6b44c09d18b75705ee806
- object_id: delivery
  role: modeling_delivery
  required: true
  ref: delivery.md
  digest: 1faad3e1efd3fda7209c451a27fe128a6266358ec0d711f2fff85a4cfa7a6c1f
- object_id: suite2
  role: suite
  required: true
  ref: suite2.md
  digest: 86c9fad95a94187906f10cfa925cf0b45fcb1c933f7c7e58c566a0142aa3b701
- object_id: suite1
  role: suite
  required: true
  ref: suite1.md
  digest: 88745f7822ce0c412a5f8904bfc5abe9535f0807e65f7f2d776473df32256426
- object_id: suite0
  role: suite
  required: true
  ref: suite0.md
  digest: 86dde16dfc99ff89e10ba1d4df14daacc6a2f3b94b42fbfcba8339741d7f5a28
- object_id: node
  role: node
  required: true
  ref: node.md
  digest: 9d4289962be6dcdb85dd212f1d0ce563b6a5259afdda2e08bcc98c811f37df0f
node_bindings:
- node_id: N
  task_id: T
  attempt: 1
  node_object_id: node
  delivery_object_id: delivery
  terminal_object_id: terminal
  suite_object_ids:
    ontology_modeling: suite0
    ontology_projection: suite1
    ontology_conformance_verification: suite2
required_scenes:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
issue_refs: []
---

Synthetic review fixture; no real authorization.
