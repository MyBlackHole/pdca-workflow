---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: review-package
template_ref: ../../../templates/review-package.md
template_digest: c1608aacfbd6c30af2c1f9a5b15100b9c6519070003059a3311411f78cf15984
shape:
  strings:
  - task_id
  - review_id
  - phase
  lists:
  - objects
  references: []
  digests:
  - baseline_digest
  positive_integers: []
  booleans: []
  mappings: []
  enums: {}
---

# review-package 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
