---
schema: pdca.asset/v1
id: ontology:entity/backup-crypto-entity
type: entity
layer: Knowledge
status: active
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
