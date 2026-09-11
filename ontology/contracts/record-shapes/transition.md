---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: transition
template_ref: ../../../templates/transition.md
template_digest: e3a4a238e830f6fab8e5bf0b3701d65262c62227a50d0ad05398cf4f828b38f4
shape:
  strings:
  - task_id
  - gate_id
  - actor_ref
  lists:
  - inputs
  references:
  - inputs_manifest_ref
  - gate_check_ref
  - writer_grant_ref
  - commit_receipt_ref
  digests:
  - baseline_digest
  - inputs_digest
  - gate_check_digest
  positive_integers:
  - attempt
  - sequence
  - observed_control_revision
  booleans: []
  mappings: []
  enums:
    decision:
    - approved
    from:
    - plan
    - do
    - check
    - act
    to:
    - do
    - check
    - act
    - archive
---

# transition 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
