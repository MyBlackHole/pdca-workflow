---
schema: pdca.asset/v2
id: ontology:domain/core-trigger-audit-derived-state-boundary
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/core-trigger-audit-derived-state-boundary/3.1.0
summary: Trigger 审计的派生状态边界
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 通读正文派生边界节，确认触发器审计边界规则完整
  evidence_level: unclassified
revision: 3.1.0
authority: reference
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# Trigger 审计的派生状态边界

审计 bcachefs 风格的 transaction trigger 时，不能只按公开 API 产生的 key type
判断是否适用。必须从写入源扩展到同一 transaction 内派生的状态：

`extent / btree pointer -> alloc -> backpointer / stripe-backpointer -> accounting /
reconcile -> journal / recovery / GC`。

内部 btree pointer 也属于触发审计范围：本地 bcachefs 把 `BKEY_TYPE_btree` 列为
transactional trigger node type，且 btree pointer key-op 使用 extent trigger。
backpointer 通常是 extent/btree-pointer trigger 写入的派生目标，而不是可独立忽略的
叶子 key。

若独立 Rust 引擎尚未具备 GC visited 模型，GC trigger 必须在依赖图中明确标为前置
条件，不可孤立移植。仅当每一条边的上游语义、当前生产路径和恢复边界均得到证明后，
才能拆分最小实现任务。

来源：T0179 partial，`records/T0179-0802-trigger-chain-applicability-audit/conclusion.md`。
