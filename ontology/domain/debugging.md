---
schema: pdca.asset/v1
id: ontology:domain/debugging
type: domain
layer: Knowledge
status: active
summary: debugging 领域知识根节点（由 ontology/domain/debugging/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# debugging（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `c-buffer-api-size_t-frame-validation` → `ontology:domain/debugging-c-buffer-api-size-t-frame-validation`
- `rpc-epoll-blocking-fd-trap` → `ontology:domain/debugging-rpc-epoll-blocking-fd-trap`
- `stream-frame-integration-traps` → `ontology:domain/debugging-stream-frame-integration-traps`
