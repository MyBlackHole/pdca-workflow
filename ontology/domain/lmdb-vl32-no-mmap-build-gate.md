---
schema: pdca.asset/v1
id: ontology:domain/lmdb-vl32-no-mmap-build-gate
type: domain
layer: Knowledge
status: active
summary: LMDB VL32 No-mmap Build Gate
domain:
- ontology:domain/lmdb
relations:
  specializes:
  - ontology:domain/lmdb
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# LMDB VL32 No-mmap Build Gate

## Rule

When a deployment requires the LMDB page-management/no-mmap branch, do not infer compliance from `MDB_NORDAHEAD`, `madvise`, or an arbitrary library path. Require an explicit include/library pair and probe the supplied header for `MDB_VL32`; reject standard system LMDB when the probe is absent.

## Adapter Boundary

Keep the MetadataStore adapter on the compatible transaction/key/value API. Do not call `mdb_env_info`, inspect mapped addresses, use `madvise`, or add map-size/read-ahead tuning that assumes the standard mmap implementation.

## Verification Boundary

Build gates and SQLite/TLS/checkpoint fallback tests can prove the safety baseline. They cannot prove no-mmap runtime correctness or performance without the actual matching `MDB_VL32` header/library. Standard mmap benchmark data must remain historical context, not no-mmap evidence.

Source: T0249 conclusion.
