---
schema: pdca.asset/v1
id: ontology:domain/data-formats
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats/1.0.0
summary: data-formats 领域知识根节点（由 ontology/domain/data-formats/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# data-formats（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `backup-tools-serialization-practice` → `ontology:domain/data-formats-backup-tools-serialization-practice`
- `mysql-innodb-physical-read-notes` → `ontology:domain/data-formats-mysql-innodb-physical-read-notes`
- `parquet-technical-reference` → `ontology:domain/data-formats-parquet-technical-reference`
- `pg-consistency-verification-method` → `ontology:domain/data-formats-pg-consistency-verification-method`
- `pg-heap-null-bitmap` → `ontology:domain/data-formats-pg-heap-null-bitmap`
- `pg-heap-physical-read-notes` → `ontology:domain/data-formats-pg-heap-physical-read-notes`
- `pg-to-parquet-path-benchmark` → `ontology:domain/data-formats-pg-to-parquet-path-benchmark`
- `t0250-mysql-parquet-physical/evidence/EVIDENCE` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-evidence`
- `t0250-mysql-parquet-physical/evidence/ac10_pg_100m_frozen_fix` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix`
- `t0250-mysql-parquet-physical/evidence/ac1_four_versions` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions`
- `t0250-mysql-parquet-physical/evidence/ac5_benchmark` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark`
- `t0250-mysql-parquet-physical/evidence/ac7_100m_benchmark` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark`
- `t0250-mysql-parquet-physical/evidence/research-report` → `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-research-report`
- `t0300-mysql-version-convert-test` → `ontology:domain/data-formats-t0300-mysql-version-convert-test`
- `t0301-pg-version-convert-test` → `ontology:domain/data-formats-t0301-pg-version-convert-test`
