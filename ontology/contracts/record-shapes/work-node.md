---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: work-node
template_ref: ../../../templates/work-node.md
template_digest: 84322c5de62e84a63d8e03fef01d5080fd1e7daab1dd0d4d9b22fed866428e71
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
