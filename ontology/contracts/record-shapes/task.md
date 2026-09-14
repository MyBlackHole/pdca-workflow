---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: task
template_ref: ../../../templates/task.md
template_digest: 7b35d783f805c6005b5bddeddc339c9d35b8d3517e8a9eb3ecfd1acc366c7da3
shape:
  strings:
  - task_id
  - work_id
  - tree_revision
  - node_id
  - scene
  - writer
  - conversation_ref
  lists: []
  references:
  - baseline
  - test_suite_ref
  - last_transition
  digests: []
  positive_integers:
  - attempt
  booleans: []
  mappings: []
  enums:
    phase:
    - archive
    execution_state:
    - completed
---

# task 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
