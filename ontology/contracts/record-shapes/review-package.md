---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: review-package
template_ref: ../../../templates/review-package.md
template_digest: b9eafaf991793ee51b60547456bc66a939e430889f5fff5008563657303583b4
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
