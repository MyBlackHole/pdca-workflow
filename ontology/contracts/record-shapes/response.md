---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: response
template_ref: ../../../templates/response.md
template_digest: 5ce838a1353f64d4c31bb3bb110ca5ad0aac752cecdd51423ceaec2c012cc4fa
shape:
  strings:
  - task_id
  - request_id
  - kind
  - phase
  - conversation_ref
  - actor_ref
  lists: []
  references:
  - subject_ref
  - source_ref
  - host_received_event_ref
  digests:
  - subject_digest
  positive_integers:
  - attempt
  booleans: []
  mappings: []
  enums:
    response:
    - confirmed
    - rejected
    - needs_change
---

# response 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
