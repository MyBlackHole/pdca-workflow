---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: test-case-binding
template_ref: ../../../templates/test-case-binding.md
template_digest: 33c31e86d76871c70d34cb9a21425278a01b66e1fc5463eb3e40321ba321aa9b
shape:
  strings:
  - binding_id
  - source_suite_revision
  - source_case_id
  - source_case_revision
  - node_id
  - scene
  - local_case_id
  - input_contract
  - input_transform
  - oracle_applicability
  lists:
  - constraint_mapping
  references:
  - source_suite_ref
  - local_suite_ref
  - effective_case_ref
  digests:
  - source_suite_digest
  - source_case_digest
  - effective_case_digest
  positive_integers: []
  booleans:
  - required
  mappings: []
  enums: {}
---

# test-case-binding 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
