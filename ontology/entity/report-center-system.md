---
schema: pdca.asset/v2
id: ontology:entity/report-center-system
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/report-center-system/3.1.0
summary: ReportCenter 系统聚合（composed_of Web + Collection）
relations:
  specializes:
  - ontology:concept/domain-entity
  composed_of:
  - ontology:entity/report-center-web-entity
  - ontology:entity/report-center-collection-entity
  relates_to:
  - ontology:domain/report-center
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# ReportCenter System
