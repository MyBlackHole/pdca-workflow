---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: dependency-snapshot
template_ref: ../../../templates/dependency-snapshot.md
template_digest: aa88681af88c6f7c77de0279f039499bb2e4d497e1c8e139329ac02e11bf4053
shape:
  strings:
  - work_id
  - tree_revision
  - graph_revision
  - scope
  - producer_ref
  lists:
  - vertices
  - edges
  references: []
  digests: []
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# dependency-snapshot 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
