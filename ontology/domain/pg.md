---
schema: pdca.asset/v1
id: ontology:domain/pg
type: domain
layer: Knowledge
status: active
summary: pg 领域知识根节点（由 ontology/domain/pg/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# pg（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `backup-recovery-wal-replay` → `ontology:domain/pg-backup-recovery-wal-replay`
- `pgwrecover-implementation` → `ontology:domain/pg-pgwrecover-implementation`
- `toast-compressed-varlena-layout` → `ontology:domain/pg-toast-compressed-varlena-layout`
- `visibility-clog-infomask` → `ontology:domain/pg-visibility-clog-infomask`
