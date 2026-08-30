---
schema: pdca.asset/v1
id: ontology:domain/rdb-config
type: domain
layer: Knowledge
status: active
summary: rdb-config 领域知识根节点（由 knowledge/rdb-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# rdb-config（领域知识根节点）

由 `knowledge/rdb-config/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `audit-findings` → `ontology:domain/rdb-config-audit-findings`
- `optim-roadmap` → `ontology:domain/rdb-config-optim-roadmap`
- `wire-tool-config-to-registry` → `ontology:domain/rdb-config-wire-tool-config-to-registry`
