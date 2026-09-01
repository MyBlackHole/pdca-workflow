---
schema: pdca.asset/v1
id: ontology:entity/backup-system
type: entity
layer: Knowledge
status: active
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
