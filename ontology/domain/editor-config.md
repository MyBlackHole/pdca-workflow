---
schema: pdca.asset/v1
id: ontology:domain/editor-config
type: domain
layer: Knowledge
status: active
summary: editor-config 领域知识根节点（由 knowledge/editor-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# editor-config（领域知识根节点）

由 `knowledge/editor-config/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `neovim-config-audit` → `ontology:domain/editor-config-neovim-config-audit`
