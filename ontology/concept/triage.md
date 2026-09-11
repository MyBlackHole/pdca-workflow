---
schema: pdca.asset/v2
id: ontology:concept/triage
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/triage/3.1.0
summary: 分诊：状态机、Agent 就绪简要、AI 免责声明
relations:
  specializes:
  - ontology:principle
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# Triage

分诊：状态机、Agent 就绪简要、AI 免责声明
