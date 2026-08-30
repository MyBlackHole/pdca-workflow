---
schema: pdca.asset/v1
id: ontology:domain/backup
type: domain
layer: Knowledge
status: active
summary: backup 领域知识根节点（由 knowledge/backup/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# backup（领域知识根节点）

由 `knowledge/backup/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `gs-roach-gm-encrypt-support` → `ontology:domain/backup-gs-roach-gm-encrypt-support`
- `ob-backup-gm-encrypt-support` → `ontology:domain/backup-ob-backup-gm-encrypt-support`
- `xtrabackup-incremental-schemes` → `ontology:domain/backup-xtrabackup-incremental-schemes`
