---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: tree-manifest
template_ref: ../../../templates/tree-manifest.md
template_digest: 6436a62efbe576e2f22b6ce0c54957cc1b3614549cddb6dd35da500dfccb721c
shape:
  strings:
  - work_id
  - tree_revision
  - proposal_id
  - root_node_id
  lists:
  - objects
  - node_bindings
  - required_scenes
  references:
  - tree_spec
  digests: []
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# tree-manifest 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
