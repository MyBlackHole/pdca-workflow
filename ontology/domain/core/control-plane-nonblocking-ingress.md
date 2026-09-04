---
schema: pdca.asset/v1
id: ontology:domain/control-plane-nonblocking-ingress
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/control-plane-nonblocking-ingress/1.0.0
summary: control-plane-nonblocking-ingress 领域知识根节点（由 ontology/domain/control-plane-nonblocking-ingress/
  迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "运行 grep -q 'control-plane-nonblocking-ingress（领域知识根节点）' ontology/domain/core/control-plane-nonblocking-ingress.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


# control-plane-nonblocking-ingress（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `v81-control-frame-nonblocking` → `ontology:domain/control-plane-nonblocking-ingress-v81-control-frame-nonblocking`
- `v81-control-plane-perf-fastpath` → `ontology:domain/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath`
