---
schema: pdca.fixture-local-delta/v1
fixture_only: true
scope:
  work_id: FIX-A
  tree_revision: tree-2
  node_id: Range
base_ref:
  library_id: FIX-LIB
  definition_id: FIX/Range
  revision: r1
  content_ref: library/versions/range/r1/definition.md
  content_digest:
    algorithm: sha256
    value: f915023b583367b115f3c4b416e2e26e2dcca0b21124e207088a450f63c3749b
  manifest_ref: library/versions/range/r1/manifest.md
  manifest_digest:
    algorithm: sha256
    value: 6a2b99de554a75bf6059bd14d301ab385022009e4b682e31e1577b3786c65466
  binding_kind: baseline_snapshot
  applicability:
    units: bytes
    requires_source_review_in_real_task: true
  constraint_bindings:
  - source_constraint_id: C_RANGE
    local_constraint_id: A-C_RANGE
    applies: true
    required: true
    source_ref: library/versions/range/r1/definition.md
    test_case_refs:
    - FIX/P-END
    - FIX/N-END
  - source_constraint_id: C_PURE
    local_constraint_id: A-C_PURE
    applies: true
    required: true
    source_ref: library/versions/range/r1/definition.md
    test_case_refs:
    - FIX/P-END
    - FIX/N-END
  excluded_constraints: []
  claim_review_refs:
  - FIXTURE_ONLY-NO-PRODUCTION-REVIEW
  adoption_id: FIX-A-Range
decision: reuse
instance_parameters:
  capacity_N: 16
semantic_change: false
requires_real_confirmation: true
---

capacity=16是已有域内实例化。若加入“只允许4字节对齐请求”，必须声明local_extension和新接口/不兼容范围、增加正反例，不能自动写回共享Range。此文件不是已确认tree-2。
