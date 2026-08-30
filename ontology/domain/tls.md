---
schema: pdca.asset/v1
id: ontology:domain/tls
type: domain
layer: Knowledge
status: active
summary: tls 领域知识根节点（由 knowledge/tls/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# tls（领域知识根节点）

由 `knowledge/tls/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `cert-dual-format-and-path-unify` → `ontology:domain/tls-cert-dual-format-and-path-unify`
- `client-ctx-cache-concurrency` → `ontology:domain/tls-client-ctx-cache-concurrency`
- `handshake-dup-impl-length-contract` → `ontology:domain/tls-handshake-dup-impl-length-contract`
- `handshake-reject-frame-consistency` → `ontology:domain/tls-handshake-reject-frame-consistency`
