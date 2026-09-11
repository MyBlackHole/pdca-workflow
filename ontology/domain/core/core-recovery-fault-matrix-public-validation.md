---
schema: pdca.asset/v2
id: ontology:domain/core-recovery-fault-matrix-public-validation
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/core-recovery-fault-matrix-public-validation/3.1.0
summary: Recovery fault matrix and public derived validation
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
  testable_signal: 通读正文故障矩阵节，确认恢复验证覆盖规则完整
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

# Recovery fault matrix and public derived validation

在 journal replay → derived rebuild → publication 的 recovery 顺序中，派生状态校验必须保持
只读，并可通过公开 API 独立调用。fault 注入应绑定三个边界：replay 后、rebuild 阶段、publication
前；任一 fault 都不得返回成功恢复对象。结构化 mismatch 至少区分 invalid pointer、generation、
duplicate backpointer、alloc set 和 backpointer set，便于测试和上层诊断。
