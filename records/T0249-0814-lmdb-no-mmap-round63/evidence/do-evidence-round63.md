# Round 63 Do Evidence

## Feature Probe And Build Gates

- CMake with `/usr/include/lmdb.h` and `/usr/lib/liblmdb.so` failed during `BACKUPSTREAM_LMDB_HAS_VL32`: the header does not expose `MDB_VL32`.
- Make with `LMDB=1 LMDB_NO_MMAP=1 LMDB_CFLAGS=-I/usr/include LMDB_LDLIBS=/usr/lib/liblmdb.so` failed while compiling `metadata_store.cpp`: `LMDB support requires the MDB_VL32 page-management branch`.
- Make without LMDB, TLS ON, completed after a serialized rerun. Make TLS OFF completed. CMake TLS OFF/LMDB OFF completed.

## API Surface

- `src/metadata_store.cpp` no longer includes `sys/mman.h`, `madvise`, `mdb_env_info`, `MDB_NORDAHEAD`, or `mdb_env_set_mapsize`.
- SQLite keeps its explicit `PRAGMA mmap_size=0`; this is unrelated to the LMDB backend.
- `git diff --check` and `tests/style_check.sh .` passed.

## Fallback And Regression

- `make TLS=1 BUILD=build-round63 test`: PASS. Unit, core integration, tree, production, SQLite metadata, system RPC, session pool, data lane, callback reactor, TLS reactor/data/control/tree suites, and style all passed.
- `make TLS=0 BUILD=build-round63-tls0`: PASS.
- `cmake --build build-round63-cmake-off`: PASS.
- `tests/metadata_index_integration.sh ./build-round63 sqlite`: PASS.
- `tests/metadata_backend_integration.sh ./build-round63 sqlite`: PASS.
- `tests/tls_tree_checkpoint_resume_integration.sh ./build-round63`: PASS; `skipped=67327`, `resent_files=32673`.

## Explicit Coverage Gap

- The environment has only the standard mmap LMDB header/library and no `MDB_VL32` no-mmap branch. Therefore no-mmap LMDB runtime integration, old-cache rebuild against that branch, five-pair 100k no-mmap benchmark, RSS, and no-mmap-vs-SQLite performance comparison were not run.
- T0248 standard-mmap LMDB measurements remain historical baseline only and are not reported as Round 63 no-mmap results.
