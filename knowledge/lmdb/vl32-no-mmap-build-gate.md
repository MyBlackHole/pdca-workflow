# LMDB VL32 No-mmap Build Gate

## Rule

When a deployment requires the LMDB page-management/no-mmap branch, do not infer compliance from `MDB_NORDAHEAD`, `madvise`, or an arbitrary library path. Require an explicit include/library pair and probe the supplied header for `MDB_VL32`; reject standard system LMDB when the probe is absent.

## Adapter Boundary

Keep the MetadataStore adapter on the compatible transaction/key/value API. Do not call `mdb_env_info`, inspect mapped addresses, use `madvise`, or add map-size/read-ahead tuning that assumes the standard mmap implementation.

## Verification Boundary

Build gates and SQLite/TLS/checkpoint fallback tests can prove the safety baseline. They cannot prove no-mmap runtime correctness or performance without the actual matching `MDB_VL32` header/library. Standard mmap benchmark data must remain historical context, not no-mmap evidence.

Source: T0249 conclusion and ADR-0022.
