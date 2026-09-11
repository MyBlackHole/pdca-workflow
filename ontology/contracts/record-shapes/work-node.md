---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: work-node
template_ref: ../../../templates/work-node.md
template_digest: ecaa74785e6ca58c85c0911526e5eebad4f337a94ff3a5855c1674612e2bf6d0
shape:
  strings:
  - work_id
  - tree_revision
  - node_id
  - node_revision
  lists: []
  references: []
  digests: []
  positive_integers: []
  booleans: []
  mappings:
  - test_suites
  - decomposition
  enums: {}
---

# work-node 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
