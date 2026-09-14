---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: archive-receipt
template_ref: ../../../templates/archive-receipt.md
template_digest: bad1580c3e58c3b40764f9d57b36622ed5e63d59c400ba7c6d8b28f369350fa0
shape:
  strings:
  - task_id
  - work_id
  - tree_revision
  - node_id
  - scene
  - receipt_id
  lists: []
  references:
  - last_transition_ref
  - delivery_ref
  - chain_check_ref
  - record_handoff_ref
  - host_event_ref
  - provenance_ref
  digests:
  - last_transition_digest
  - delivery_digest
  positive_integers:
  - attempt
  booleans: []
  mappings: []
  enums:
    result:
    - completed
---

# archive-receipt 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
