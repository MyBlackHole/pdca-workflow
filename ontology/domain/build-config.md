---
schema: pdca.asset/v1
id: ontology:domain/build-config
type: domain
layer: Knowledge
status: active
summary: build-config 领域知识根节点（由 ontology/domain/build-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# build-config（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `go-module-in-xmake` → `ontology:domain/build-config-go-module-in-xmake`
- `hide-static-lib-symbols` → `ontology:domain/build-config-hide-static-lib-symbols`
