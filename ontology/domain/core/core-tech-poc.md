---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-tech-poc/1.0.0
summary: core-tech-poc 领域知识根节点（由 ontology/domain/core-tech-poc/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件核心相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# core-tech-poc（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `aead-auth-encryption` → `ontology:domain/core-tech-poc-aead-auth-encryption`
- `bloom-filter-dedup` → `ontology:domain/core-tech-poc-bloom-filter-dedup`
- `frame-multiplexing` → `ontology:domain/core-tech-poc-frame-multiplexing`
- `hash-selection` → `ontology:domain/core-tech-poc-hash-selection`
- `reed-solomon-erasure` → `ontology:domain/core-tech-poc-reed-solomon-erasure`
- `zero-copy-transfer` → `ontology:domain/core-tech-poc-zero-copy-transfer`
