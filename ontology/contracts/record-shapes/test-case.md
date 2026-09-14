---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: test-case
template_ref: ../../../templates/test-case.md
template_digest: 0c0a7c6fcf5be1cf52bbd05ca343392bf834344ced84f22ba7c17fa0c286fdd3
shape:
  strings:
  - case_id
  - node_id
  - scene
  - revision
  - suite_ref
  - category
  - preconditions
  - action
  - observation
  - failure_signature
  - cleanup
  lists:
  - constraint_ids
  references: []
  digests: []
  positive_integers: []
  booleans:
  - required
  mappings:
  - inputs
  - expected
  - oracle
  enums: {}
---

# test-case 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
