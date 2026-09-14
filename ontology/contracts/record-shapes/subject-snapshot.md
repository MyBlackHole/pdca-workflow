---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: subject-snapshot
template_ref: ../../../templates/subject-snapshot.md
template_digest: f760c101a995c43e0fa6fcf2644ad6be449e04c21a71fdb2f0b75f44c34ef6ee
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
