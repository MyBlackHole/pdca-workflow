---
schema: pdca.asset/v1
id: ontology:domain/mysql
type: domain
layer: Knowledge
status: active
summary: mysql 领域知识根节点（由 knowledge/mysql/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# mysql（领域知识根节点）

由 `knowledge/mysql/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `backup-recovery-consistency` → `ontology:domain/mysql-backup-recovery-consistency`
- `normal-shutdown-visibility-scope` → `ontology:domain/mysql-normal-shutdown-visibility-scope`
- `schema-nullable-contract` → `ontology:domain/mysql-schema-nullable-contract`
