---
schema: pdca.asset/v1
id: ontology:domain/report-center
type: domain
layer: Knowledge
status: active
summary: report-center 领域知识根节点（由 ontology/domain/report-center/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件报表相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# report-center（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `async-export-distributed-quota-patterns` → `ontology:domain/report-center-async-export-distributed-quota-patterns`
- `auth-rpc-compensation-patterns` → `ontology:domain/report-center-auth-rpc-compensation-patterns`
- `cli-from-scratch-lazy-import` → `ontology:domain/report-center-cli-from-scratch-lazy-import`
- `db-adapter-pg-practices` → `ontology:domain/report-center-db-adapter-pg-practices`
- `deployment-assembly-patterns` → `ontology:domain/report-center-deployment-assembly-patterns`
- `report-center-decomposition-index` → `ontology:domain/report-center-report-center-decomposition-index`
- `report-web-report-sql-patterns` → `ontology:domain/report-center-report-web-report-sql-patterns`
