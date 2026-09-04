---
schema: pdca.asset/v1
id: ontology:domain/rdb-config
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/rdb-config/1.0.0
summary: rdb-config 领域知识根节点（由 ontology/domain/rdb-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "运行 grep -q '子主题' ontology/domain/report-center/rdb-config.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


# rdb-config（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `audit-findings` → `ontology:domain/rdb-config-audit-findings`
- `optim-roadmap` → `ontology:domain/rdb-config-optim-roadmap`
- `wire-tool-config-to-registry` → `ontology:domain/rdb-config-wire-tool-config-to-registry`
