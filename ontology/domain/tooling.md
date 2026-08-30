---
schema: pdca.asset/v1
id: ontology:domain/tooling
type: domain
layer: Knowledge
status: active
summary: tooling 领域知识根节点（由 knowledge/tooling/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# tooling（领域知识根节点）

由 `knowledge/tooling/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `cpp-api-style-mechanical-refactor-pitfalls` → `ontology:domain/tooling-cpp-api-style-mechanical-refactor-pitfalls`
- `layered-checker-shortcircuit-alignment` → `ontology:domain/tooling-layered-checker-shortcircuit-alignment`
