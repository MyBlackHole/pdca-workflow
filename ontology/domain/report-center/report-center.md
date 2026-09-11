---
schema: pdca.asset/v2
id: ontology:domain/report-center
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/report-center/3.1.0
summary: report-center 领域知识根节点（由 ontology/domain/report-center/ 迁移）
relations:
  relates_to:
  - ontology:concept/pdca
  instance_of:
  - ontology:concept/knowledge-artifact
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# report-center（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `async-export-distributed-quota-patterns` → `ontology:domain/report-center-async-export-distributed-quota-patterns`
- `auth-rpc-compensation-patterns` → `ontology:domain/report-center-auth-rpc-compensation-patterns`
- `cli-from-scratch-lazy-import` → `ontology:domain/report-center-cli-from-scratch-lazy-import`
- `db-adapter-pg-practices` → `ontology:domain/report-center-db-adapter-pg-practices`
- `deployment-assembly-patterns` → `ontology:domain/report-center-deployment-assembly-patterns`
- `report-center-decomposition-index` → `ontology:domain/report-center-report-center-decomposition-index`
- `report-web-report-sql-patterns` → `ontology:domain/report-center-report-web-report-sql-patterns`
