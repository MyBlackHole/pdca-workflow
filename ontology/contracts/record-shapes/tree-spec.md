---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: tree-spec
template_ref: ../../../templates/tree-spec.md
template_digest: 030526198635576767d58cfa75764561610f982b4dda02a6c087f50795febe85
shape:
  strings:
  - work_id
  - tree_revision
  - proposal_id
  - root_node_id
  - goal
  lists:
  - nodes
  - requirement_ownership
  references:
  - original_request_ref
  - protocol_baseline_ref
  - subject_snapshot_ref
  digests: []
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# tree-spec 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
