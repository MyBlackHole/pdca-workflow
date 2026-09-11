---
schema: pdca.fixture-work/v1
fixture_only: true
work_id: FIX-C
tree_revision: tree-1
nodes:
- node_id: Root
  parent_node_id: null
  children:
  - Range
  - Writer
- node_id: Range
  parent_node_id: Root
  children: []
  definition_refs:
  - library_id: FIX-LIB
    definition_id: FIX/Range
    revision: r2
    content_ref: library/versions/range/r2/definition.md
    content_digest:
      algorithm: sha256
      value: 595a6d97dc127fe80f4a2561123f9308ea1e61cfedf014b860df6258a1f86e38
    manifest_ref: library/versions/range/r2/manifest.md
    manifest_digest:
      algorithm: sha256
      value: 6170e2b1c9df37745751ce9abca7910dfe52f9132e02804d232ffcda6e4da49f
    binding_kind: baseline_snapshot
    applicability:
      units: bytes
      requires_source_review_in_real_task: true
    constraint_bindings:
    - source_constraint_id: C_RANGE
      local_constraint_id: C-C_RANGE
      applies: true
      required: true
      source_ref: library/versions/range/r2/definition.md
      test_case_refs:
      - FIX/P-END
      - FIX/N-END
    - source_constraint_id: C_PURE
      local_constraint_id: C-C_PURE
      applies: true
      required: true
      source_ref: library/versions/range/r2/definition.md
      test_case_refs:
      - FIX/P-END
      - FIX/N-END
    excluded_constraints: []
    claim_review_refs:
    - FIXTURE_ONLY-NO-PRODUCTION-REVIEW
    adoption_id: FIX-C-Range
- node_id: Writer
  parent_node_id: Root
  children: []
task_result: NOT_RUN
scope: structure_and_reference_fixture_only
---

# 工作C教学树

Root/Range/Writer各有建模、实现、独立审查任务的义务，但本文件未运行这些任务，未补造task/Agent/确认。只有Range的定义绑定实际固定字节，其余节点未补全suite，不能直接当生产树。
