---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: baseline
template_ref: ../../../templates/baseline.md
template_digest: 3eb56c27a9219e5f508f65a9edf4e4f6b9238fc7e8acd66a17b212fbf276eedd
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
