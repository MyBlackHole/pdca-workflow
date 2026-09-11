---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: request
template_ref: ../../../templates/request.md
template_digest: 166e627f689dd263d84b80ed4c4ef87a7d3f4b66a8afb432279c40fa0f405796
shape:
  strings:
  - task_id
  - request_id
  - kind
  - phase
  - conversation_ref
  - producer_ref
  lists: []
  references:
  - subject_ref
  digests:
  - subject_digest
  positive_integers:
  - attempt
  booleans: []
  mappings: []
  enums:
    kind:
    - plan_confirmation
    - check_confirmation
    phase:
    - plan
    - check
---

# request 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
