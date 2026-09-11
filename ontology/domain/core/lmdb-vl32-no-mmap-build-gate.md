---
schema: pdca.asset/v2
id: ontology:domain/lmdb-vl32-no-mmap-build-gate
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/lmdb-vl32-no-mmap-build-gate/3.1.0
summary: LMDB VL32 No-mmap Build Gate
domain:
- ontology:domain/lmdb
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/lmdb
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 运行 grep -q 'lmdb-vl32' ontology/domain/core/lmdb-vl32-no-mmap-build-gate.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# LMDB VL32 No-mmap Build Gate

## Rule

When a deployment requires the LMDB page-management/no-mmap branch, do not infer compliance from `MDB_NORDAHEAD`, `madvise`, or an arbitrary library path. Require an explicit include/library pair and probe the supplied header for `MDB_VL32`; reject standard system LMDB when the probe is absent.

## Adapter Boundary

Keep the MetadataStore adapter on the compatible transaction/key/value API. Do not call `mdb_env_info`, inspect mapped addresses, use `madvise`, or add map-size/read-ahead tuning that assumes the standard mmap implementation.

## Verification Boundary

Build gates and SQLite/TLS/checkpoint fallback tests can prove the safety baseline. They cannot prove no-mmap runtime correctness or performance without the actual matching `MDB_VL32` header/library. Standard mmap benchmark data must remain historical context, not no-mmap evidence.

Source: T0249 conclusion.
