---
schema: pdca.asset/v1
id: ontology:entity/backup-xtrabackup-entity
type: entity
layer: Knowledge
status: active
summary: Backup Xtrabackup 实体（BackupSystem 叶）
attributes:
  - name: demo_backup
    desc: Demo backup 桩
    constraint: GET /api/backup/demo 返回 {"backup":1}
    testable_signal: "运行 python3 -m pytest tests/test_backup_demo.py -v 检查桩返回 {backup:1}，且 scaffold 通过"
relations:
  specializes:
    - ontology:concept/domain-entity
---

# Backup Xtrabackup 实体
