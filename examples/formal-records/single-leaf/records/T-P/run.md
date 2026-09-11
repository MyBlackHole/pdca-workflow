---
schema: pdca.test-run/v3
run_id: RUN-P
task_id: T-P
work_id: W
tree_revision: TR
node_id: N
scene: ontology_projection
attempt: 1
repair_iteration: 0
suite_ref: ../../suites/node-projection.md
suite_digest: 2767a507098cdb00dd6fbe15951011cb351299f3ed41d881aed00fa7f66aea2d
artifact_ref: ../../artifacts/projection.md
artifact_digest: 4556a869f8652a3cf5cbcfb417b08b5d1f7f7c46c263a8c29a484c93ab371359
child_artifacts: []
environment_ref:
  ref: ../../inputs/host-source.md
  digest: 977ecf358f530e98b5b8059ac5aed2d7bd1cbde5746abb3c527333e336d6b5f9
started_at: null
time_source: null
case_results:
- case_id: PROJECTION-P
  node_id: N
  suite_id: SUITE-PROJECTION
  suite_revision: 1.0.0
  case_revision: 1.0.0
  effective_case_digest: 81c20657207f2d8eb31a17fab7cc130b7dc768c258b252d7a9ce82f8e06de047
  subject_verdict: unknown
  checker_case_result: pass
  checker_mutation_result: null
  result: pass
  observation_ref:
    ref: observations/PROJECTION-P.md
    digest: 4162028558e6b659cbc0e8b7accd4a652522f0f5d0553d0417fea35248e54f98
- case_id: PROJECTION-N
  node_id: N
  suite_id: SUITE-PROJECTION
  suite_revision: 1.0.0
  case_revision: 1.0.0
  effective_case_digest: 8195fef66d13382d7d3aae789fee7d83c51351f446f270f694dfdb44412e2938
  subject_verdict: unknown
  checker_case_result: pass
  checker_mutation_result: null
  result: pass
  observation_ref:
    ref: observations/PROJECTION-N.md
    digest: 774da99661461c232a61325da9739902130d202763f213c5e03a9ff275031faa
mutation_run: false
mutant_id: null
raw_evidence_refs:
- ref: observations/PROJECTION-P.md
  digest: 4162028558e6b659cbc0e8b7accd4a652522f0f5d0553d0417fea35248e54f98
- ref: observations/PROJECTION-N.md
  digest: 774da99661461c232a61325da9739902130d202763f213c5e03a9ff275031faa
protocol_revision: 3.4.4
effective_case_refs:
- ref: ../../cases/projection/PROJECTION-P.md
  digest: 81c20657207f2d8eb31a17fab7cc130b7dc768c258b252d7a9ce82f8e06de047
- ref: ../../cases/projection/PROJECTION-N.md
  digest: 8195fef66d13382d7d3aae789fee7d83c51351f446f270f694dfdb44412e2938
regression_extension_refs: []
checker_ref: ../../inputs/checker.md
checker_digest: 274f675b87ab3926f2821320058ac69a85bd67e1ddf749de26c802d0939438c5
visible_input_manifest_ref:
  ref: visible-inputs.md
  digest: a3b2cd834cc29f02bb8637b9b7d5f1a00b8fc37809aa1728ec8565afbfc18af5
fixture_validation_refs: []
previous_run_ref: null
repair_kind: null
repair_diff_ref: null
evidence_manifest_ref:
  ref: evidence.md
  digest: fd71898ad5739388ee6c929c41982ba895e245a125c63014329a26c1ba52d4d5
retention_check_ref: null
---

合成教学记录（fixture），不是实际 Agent 运行、真实用户批准或宿主事实。此处 pass 仅为待核对的合成记录字段；生产可用性未取得。
