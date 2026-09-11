---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.10
profile: fixed_formal_record_example
record_kind: conformance-review
template_ref: ../../../templates/conformance-review.md
template_digest: 8a334b9ab131df814856dc1932d7a4c81c36d34a89d5771c0208639a6d02c4b0
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
