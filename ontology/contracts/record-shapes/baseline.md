---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: baseline
template_ref: ../../../templates/baseline.md
template_digest: 0d0788b6e7b31a8c4886be32111aaf18a20a2c412957876728edf608ef955f23
shape:
  strings:
  - task_id
  - work_id
  - tree_revision
  - node_id
  - scene
  - baseline_id
  - goal_statement
  lists: []
  references:
  - original_request_ref
  - protocol_baseline_ref
  - subject_snapshot_ref
  digests: []
  positive_integers:
  - attempt
  booleans: []
  mappings: []
  enums: {}
---

# baseline 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
