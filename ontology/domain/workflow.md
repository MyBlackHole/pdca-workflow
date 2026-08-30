---
schema: pdca.asset/v1
id: ontology:domain/workflow
type: domain
layer: Knowledge
status: active
summary: workflow 领域知识根节点（由 ontology/domain/workflow/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# workflow（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `code-review-dual-axis` → `ontology:domain/workflow-code-review-dual-axis`
- `skill-invocation-convention` → `ontology:domain/workflow-skill-invocation-convention`
