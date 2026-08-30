---
schema: pdca.asset/v1
id: ontology:domain/benchmark
type: domain
layer: Knowledge
status: active
summary: benchmark 领域知识根节点（由 knowledge/benchmark/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# benchmark（领域知识根节点）

由 `knowledge/benchmark/` 逐文件迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `build-profile-baseline-matching` → `ontology:domain/benchmark-build-profile-baseline-matching`
- `paired-comparison-noise` → `ontology:domain/benchmark-paired-comparison-noise`
- `small-pack-streaming-decode` → `ontology:domain/benchmark-small-pack-streaming-decode`
- `small-writer-pool-parallelism` → `ontology:domain/benchmark-small-writer-pool-parallelism`
