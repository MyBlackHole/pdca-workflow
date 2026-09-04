---
schema: pdca.asset/v1
id: ontology:domain/editor-config
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/editor-config/1.0.0
summary: editor-config 领域知识根节点（由 ontology/domain/editor-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "运行 grep -q 'editor-config（领域知识根节点）' ontology/domain/core/editor-config.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


# editor-config（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `neovim-config-audit` → `ontology:domain/editor-config-neovim-config-audit`
