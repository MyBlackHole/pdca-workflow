---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: dependency-check
template_ref: ../../../templates/dependency-check.md
template_digest: 014da8fa23fcd783ef671361f5d1764b0961dd57fe71a4a98d0ca3b212b181b7
shape:
  strings:
  - check_id
  - work_id
  - tree_revision
  - graph_revision
  - checkpoint
  - algorithm
  - checker_ref
  lists: []
  references:
  - graph_ref
  digests:
  - graph_digest
  positive_integers: []
  booleans: []
  mappings: []
  enums:
    result:
    - acyclic
    - cyclic
    - invalid
    - unknown
---

# dependency-check 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
