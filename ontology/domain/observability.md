---
schema: pdca.asset/v1
id: ontology:domain/observability
type: domain
layer: Knowledge
status: active
summary: observability 领域知识根节点（由 knowledge/observability/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# observability（领域知识根节点）

由 `knowledge/observability/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `structured-logging-jsonl-rotation` → `ontology:domain/observability-structured-logging-jsonl-rotation`
