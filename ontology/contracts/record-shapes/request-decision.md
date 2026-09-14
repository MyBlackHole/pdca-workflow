---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: request-decision
template_ref: ../../../templates/request-decision.md
template_digest: ad3efd387aed51951a5c9f9ed18e9116fbb1dabd0099f40f48cdcb38c64bbd77
shape:
  strings:
  - decision_id
  - task_id
  - request_id
  - kind
  - phase
  - conversation_ref
  - decision_time
  lists: []
  references:
  - subject_ref
  - response_ref
  - source_ref
  - time_source_ref
  - backend_order_receipt_ref
  digests:
  - request_digest
  - subject_digest
  positive_integers:
  - attempt
  - control_revision
  booleans: []
  mappings: []
  enums:
    scope_kind:
    - task
    terminal_state:
    - consumed
    response:
    - confirmed
    - rejected
    - needs_change
---

# request-decision 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
