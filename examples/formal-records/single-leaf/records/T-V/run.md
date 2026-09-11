---
schema: pdca.test-run/v3
run_id: RUN-V
task_id: T-V
work_id: W
tree_revision: TR
node_id: N
scene: ontology_conformance_verification
attempt: 1
repair_iteration: 0
suite_ref: ../../suites/node-verification.md
suite_digest: 9f10bd4c2556f211da7bf71a72cae9498604033a10f536ec0082f34dc628b156
artifact_ref: ../../artifacts/verification.md
artifact_digest: 6e91e0d5247529d13af2fc123a8f9203c09c8e5936bb699bea9d3b4c5b856f93
child_artifacts: []
environment_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
started_at: null
time_source: null
case_results:
- case_id: VERIFICATION-P
  node_id: N
  suite_id: SUITE-VERIFICATION
  suite_revision: 1.0.0
  case_revision: 1.0.0
  effective_case_digest: 92f5d01900256e89afd9d8f0caa7d5830ccbb5cb1f8be0bafb9cff0584a5e54e
  subject_verdict: unknown
  checker_case_result: pass
  checker_mutation_result: null
  result: pass
  observation_ref:
    ref: observations/VERIFICATION-P.md
    digest: 7151a393976bf44ad587e24c242c96472afa07a77d6f4af2e89f6b3b23e2c292
- case_id: VERIFICATION-N
  node_id: N
  suite_id: SUITE-VERIFICATION
  suite_revision: 1.0.0
  case_revision: 1.0.0
  effective_case_digest: 10216607d495ccd9085409e17b57d4c7c81b284ac7add58e20acffdb2de4f709
  subject_verdict: unknown
  checker_case_result: pass
  checker_mutation_result: null
  result: pass
  observation_ref:
    ref: observations/VERIFICATION-N.md
    digest: 92e8259ba7145793bb3a4f46fbdcf3e3b4afaafb2053c9b92c61c5a1694bb6f4
mutation_run: false
mutant_id: null
raw_evidence_refs:
- ref: observations/VERIFICATION-P.md
  digest: 7151a393976bf44ad587e24c242c96472afa07a77d6f4af2e89f6b3b23e2c292
- ref: observations/VERIFICATION-N.md
  digest: 92e8259ba7145793bb3a4f46fbdcf3e3b4afaafb2053c9b92c61c5a1694bb6f4
protocol_revision: 3.4.4
effective_case_refs:
- ref: ../../cases/verification/VERIFICATION-P.md
  digest: 92f5d01900256e89afd9d8f0caa7d5830ccbb5cb1f8be0bafb9cff0584a5e54e
- ref: ../../cases/verification/VERIFICATION-N.md
  digest: 10216607d495ccd9085409e17b57d4c7c81b284ac7add58e20acffdb2de4f709
regression_extension_refs: []
checker_ref: ../../inputs/checker.md
checker_digest: 274f675b87ab3926f2821320058ac69a85bd67e1ddf749de26c802d0939438c5
visible_input_manifest_ref:
  ref: visible-inputs.md
  digest: 796b1765de72b1d672fbb5d68976545620e888e4c6622e09aa979ea7ba256b2a
fixture_validation_refs: []
previous_run_ref: null
repair_kind: null
repair_diff_ref: null
evidence_manifest_ref:
  ref: evidence.md
  digest: 4fc657297454cd08d4a598cb3a8d11c80423540db8b2dc96145178770f2bbbce
retention_check_ref: null
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
