---
schema: pdca.asset/v1
id: ontology:entity/backup-crypto-entity
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/backup-crypto-entity/1.0.0
summary: Backup Crypto 实体（BackupSystem 叶）
attributes:
  - name: demo_crypto
    desc: Demo crypto 桩
    constraint: GET /api/crypto/demo 返回 {"crypto":1}
    testable_signal: "运行 python3 -m pytest tests/test_crypto_demo.py -v 检查桩返回 {crypto:1}，且 scaffold 通过"
relations:
  specializes:
    - ontology:concept/domain-entity
---

# Backup Crypto 实体
