---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: test-suite
template_ref: ../../../templates/test-suite.md
template_digest: 8c05ba9c4d65493316c941251309cca702e5458c2fbb0e1d68e3fa3f360ad364
shape:
  strings:
  - suite_id
  - node_id
  - scene
  - revision
  lists:
  - case_refs
  - required_cases
  references: []
  digests: []
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# test-suite 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
