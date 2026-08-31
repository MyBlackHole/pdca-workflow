---
schema: pdca.asset/v1
id: ontology:domain/network-bandwidth-control
type: domain
layer: Knowledge
status: active
summary: network-bandwidth-control 领域知识根节点（由 ontology/domain/network-bandwidth-control/
  迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件网络相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# network-bandwidth-control（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `backup-bw-limit-algo-selection` → `ontology:domain/network-bandwidth-control-backup-bw-limit-algo-selection`
