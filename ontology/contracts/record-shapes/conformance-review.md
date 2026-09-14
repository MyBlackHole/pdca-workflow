---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: conformance-review
template_ref: ../../../templates/conformance-review.md
template_digest: 5a8bec5e2735ce35581e84ed0ab73b69a9e50b30efe6636adb9bd7dc551e1636
shape:
  strings:
  - review_task_id
  - work_id
  - tree_revision
  - node_id
  - subject_conformance
  - review_task_verdict
  - claim_scope
  lists:
  - subject_artifact_refs
  - test_run_refs
  references:
  - requirements_basis_ref
  - subject_snapshot_ref
  - coverage_ref
  digests:
  - requirements_basis_digest
  positive_integers: []
  booleans: []
  mappings: []
  enums:
    subject_conformance:
    - pass
    - fail
    - unknown
    review_task_verdict:
    - confirmed
    - partial
    - rejected
---

# conformance-review固定字段投影

按CONTRACT/REVIEW核对拟作为完整审查记录的有限字段；草稿可空但不能因此通过。字段与引用匹配不认证独立Agent、真实确认或自然语言结论。
