---
schema: pdca.asset/v1
id: ontology:domain/tls
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/tls/1.0.0
summary: tls 领域知识根节点（由 ontology/domain/tls/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件TLS相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# tls（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `cert-dual-format-and-path-unify` → `ontology:domain/tls-cert-dual-format-and-path-unify`
- `client-ctx-cache-concurrency` → `ontology:domain/tls-client-ctx-cache-concurrency`
- `handshake-dup-impl-length-contract` → `ontology:domain/tls-handshake-dup-impl-length-contract`
- `handshake-reject-frame-consistency` → `ontology:domain/tls-handshake-reject-frame-consistency`
