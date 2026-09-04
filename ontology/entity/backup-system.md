---
schema: pdca.asset/v1
id: ontology:entity/backup-system
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/backup-system/1.0.0
summary: Backup 系统聚合（composed_of Xtrabackup + Crypto）
relations:
  specializes:
    - ontology:concept/domain-entity
  composed_of:
    - ontology:entity/backup-xtrabackup-entity
    - ontology:entity/backup-crypto-entity
  relates_to:
    - ontology:domain/backup
---

# Backup System
