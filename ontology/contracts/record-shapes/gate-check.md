---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: gate-check
template_ref: ../../../templates/gate-check.md
template_digest: 2573ff0e445e08df5fb2fcf3a8b44482b7491b2a4ccad1a6029ca389ad815e11
shape:
  strings:
  - check_id
  - task_id
  - gate_id
  lists:
  - checks
  references:
  - subject_ref
  digests:
  - subject_digest
  positive_integers:
  - attempt
  - observed_control_revision
  booleans: []
  mappings: []
  enums:
    result:
    - ready
    - not_ready
---

# gate-check 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
