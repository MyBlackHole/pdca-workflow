# Round 63 Benchmark Status

No no-mmap benchmark is claimed. The only LMDB binary available is the standard mmap implementation at `/usr/lib/liblmdb.so`; its header does not expose `MDB_VL32`, so it is rejected by the new feature probe.

The five-pair 100k no-mmap workload, RSS, cache bytes, throughput, and comparison against SQLite remain pending until the requested `MDB_VL32` page-management branch is supplied. The standard-mmap figures from T0248 are historical context and are intentionally excluded from Round 63 acceptance.
