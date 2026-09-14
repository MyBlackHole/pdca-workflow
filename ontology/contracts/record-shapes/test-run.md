---
schema: pdca.record-shape/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
record_kind: test-run
template_ref: ../../../templates/test-run.md
template_digest: 925245a0e898f99c0dbe07edff15f784361aa48fbfc98e90b6b76968a6bd217e
shape:
  strings:
  - task_id
  - work_id
  - tree_revision
  - node_id
  - scene
  - run_id
  lists:
  - case_results
  - effective_case_refs
  - raw_evidence_refs
  references:
  - suite_ref
  - artifact_ref
  - checker_ref
  - visible_input_manifest_ref
  - evidence_manifest_ref
  digests:
  - suite_digest
  - artifact_digest
  - checker_digest
  positive_integers:
  - attempt
  booleans:
  - mutation_run
  mappings: []
  enums: {}
---

# test-run 固定记录字段投影

按需读取；继承[CONTRACT-01](../../concept/pdca-execution-contract.md#contract-fixed-records)。仅覆盖已列profile；未列字段不自动成为必填，草稿不作为完成记录核验。schema沿用正式模板，不另造简化字段。
