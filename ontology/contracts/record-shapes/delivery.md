---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: delivery
template_ref: ../../../templates/delivery.md
template_digest: e959a7ac78a003d785b8d81b1c9fb499ab0c787620fd8caa00aa6c49c30a5a09
shape:
  strings:
  - task_id
  - work_id
  - tree_revision
  - node_id
  - scene
  lists:
  - artifact_refs
  - test_run_refs
  references:
  - suite_ref
  digests: []
  positive_integers:
  - attempt
  booleans:
  - node_local_pass
  mappings: []
  enums:
    task_verdict:
    - confirmed
    - partial
    - rejected
    delivery_profile:
    - full
---

# delivery 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
