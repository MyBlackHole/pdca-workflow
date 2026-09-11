---
schema: pdca.asset/v2
id: ontology:decision/t2153-opt-backlog
type: decision
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-10
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/t2153-opt-backlog/3.1.0
summary: T2153优化 backlog 决议 Santiago：P0已修2项，P1候选8项，P2候选2项的归口与状态
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:process/flow-do
  instance_of:
  - ontology:decision
attributes:
- name: backlog_status
  desc: P0x2/P1x8/P2x2 清单归口与实施状态
  constraint: P0 已修；P1/P2 每项被 Improvement Task 认领后更新状态
  testable_signal: test $(grep -c 'P1' pdca/tasks/0910-pdca-opt-survey/research-report.md) -ge 3
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# 优化 backlog 决议（T2153）

来源：`records/T2153-0910-pdca-opt-survey/conclusion.md`，证据 `ev2153-opt-report`。

## 决议

P0（索引漂移 ✅ 已修；门禁悬空 → T2149）。
P1 八项按需立项（role/ 并入 T2149；旧分类闸与机械判定已由 `ontology_role` 和 `execution_contract` 模型取代；
退役机制、AC-5、transition 依赖校验、57 重复 ID、children 回写另立项）。
P2 两项随缘（_meta 对齐、manifest 生成器）。
