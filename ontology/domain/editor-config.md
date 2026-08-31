---
schema: pdca.asset/v1
id: ontology:domain/editor-config
type: domain
layer: Knowledge
status: active
summary: editor-config 领域知识根节点（由 ontology/domain/editor-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# editor-config（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `neovim-config-audit` → `ontology:domain/editor-config-neovim-config-audit`
