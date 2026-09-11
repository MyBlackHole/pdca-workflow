---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: subject-snapshot
template_ref: ../../../templates/subject-snapshot.md
template_digest: e5156598aa15388863a5e06170729ee165e2637b1210df619ed2b635af3b80fa
shape:
  strings:
  - snapshot_id
  - purpose
  - scope_statement
  lists:
  - required_members
  - members
  references:
  - scope_source_ref
  digests: []
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# subject-snapshot 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
