# Round 62 Do Evidence

## Backend

- `tests/metadata_index_integration.sh ./build-round62 sqlite`: PASS.
- `tests/metadata_index_integration.sh ./build-round62-lmdb lmdb`: PASS.
- `tests/metadata_backend_integration.sh ./build-round62 sqlite`: PASS.
- `tests/metadata_backend_integration.sh ./build-round62-lmdb lmdb`: PASS.
- Coverage includes baseline, unchanged scan, content change, metadata-only change, generation mismatch, failed quota run, lock ownership, and rebuild path.

## Checkpoint

- `tests/tls_tree_checkpoint_resume_integration.sh ./build-round62` with `N=100000`: PASS.
- Deterministic interruption after checkpoint file exceeded 1.8 MiB; resumed run reported `skipped=67071`, `resent_files=32929`, recovery ratio `32.929%` of clean replay.
- The fixture truncates the checkpoint tail and mutates `f000000` after confirmation; final namespace count is 100000 and mutated content matches.
- Server drains the bounded small-file queue and applies directory metadata before checkpoint ACK; old peers do not negotiate the optional capability.

## Performance

Five 100000-entry SQLite/LMDB pairs are in `benchmark-metadata-100k.log`. Means:

| operation | SQLite | LMDB | delta |
|---|---:|---:|---:|
| full build | 4.6740 s | 4.4971 s | -3.79% |
| unchanged scan | 0.3399 s | 0.2046 s | -39.8% |
| changed scan | 0.3380 s | 0.2016 s | -40.4% |

The final compact LMDB implementation reports `cache_bytes=21917696` for 100000 entries. Peak RSS remains above the requested limit: the final five-sample LMDB mean is `29899 KiB` on unchanged scan versus SQLite mean `21733 KiB` (about +38%). This is recorded as an AC-3 failure, not hidden.

## Build And Regression

- Make TLS ON: build and unit/core/tree/production/metadata/system/data-lane/style suites pass; the standalone TLS EXEC retry passes after one earlier connection-reset flake.
- Make TLS OFF: build passes.
- CMake TLS OFF/LMDB OFF: 14/14 CTest tests pass.
- CMake TLS ON/LMDB ON: 34/34 CTest tests pass in a serialized run; LMDB detection now works without explicit cache paths on `/usr/include` and `/usr/lib`.
- `git diff --check` and `tests/style_check.sh .`: PASS.
