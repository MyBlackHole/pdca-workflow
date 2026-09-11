---
schema: pdca.asset/v2
id: ontology:entity/tls-session
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/tls-session/3.1.0
summary: TLSSession：TLS 会话实体
relations:
  specializes:
  - ontology:concept/domain-entity
  composed_of:
  - ontology:entity/mtls-handshake
  - ontology:entity/x509-certificate
  configured_by:
  - ontology:entity/tls-configuration
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

# TLSSession：TLS 会话实体
