# T0252 Design：Disk-First TREE Checkpoint

## Current failure mode

`src/backupctl.cpp` currently loads the entire `.tree-checkpoint` into a byte vector and then stores every path in `unordered_map<string, uint64_t>`. This makes startup memory and retained path memory proportional to the checkpoint namespace. `pending` can also grow with a large traversal batch.

## Proposed module boundary

Move the checkpoint state machine into `src/tree_checkpoint.hpp` and `src/tree_checkpoint.cpp`. The module owns journal/index lifecycle, fingerprint matching, bounded pending state, batch numbering, recovery and metrics. The backup walk owns session I/O and invokes a small C-style module boundary for `matches`, `note`, `flush` and `close`; no walk code may inspect an internal container or entry count implementation.

## Storage model

Keep `<cache>.tree-checkpoint` as an append journal for compatibility and forensic recovery. Add a versioned sidecar `<cache>.tree-checkpoint.index.sqlite`:

```sql
CREATE TABLE meta (k TEXT PRIMARY KEY, v BLOB NOT NULL);
CREATE TABLE entries (path BLOB PRIMARY KEY, fingerprint BLOB NOT NULL);
```

The SQLite primary key is the disk B-tree. A prepared `SELECT fingerprint FROM entries WHERE path=?` handles each walk entry without loading all paths. A fixed negative `PRAGMA cache_size` bounds SQLite page cache. `meta.journal_offset` identifies the journal byte offset already materialized in the index; `generation`, `options`, `format` and `next_batch` are updated in the same transaction.

The database is opened with `SQLITE_OPEN_NOMUTEX`, `PRAGMA mmap_size=0`, a fixed negative cache size, and `synchronous=FULL`. Use the rollback journal mode (or fully checkpoint and fsync all WAL files before rename) so a sidecar migration cannot leave an orphaned `-wal` that is mistaken for a durable index. A lock file held with `flock(LOCK_EX|LOCK_NB)` prevents two backupctl processes from appending the same journal concurrently. Fingerprints are stored as an eight-byte big-endian blob, avoiding signed `sqlite3_int64` reinterpretation for values above `INT64_MAX`.

## Recovery and durability

1. Open the lock, validate journal header and sidecar metadata.
2. If metadata does not match generation/options, create a new sidecar atomically while retaining the journal until the new header/index is durable.
3. Stream records from `journal_offset`; never allocate by `st_size`. On incomplete record, truncate at its record start and stop. On invalid header/generation, discard only the incompatible sidecar and rebuild from the valid journal.
4. For a confirmed batch, send the existing remote frame and verify the same ACK. Append records, `fsync` the journal, then `BEGIN IMMEDIATE`, upsert bounded rows, update `journal_offset`, and commit. A crash between journal fsync and SQLite commit is recovered by replay; a crash after remote ACK but before local fsync retains the existing safe duplicate possibility rather than claiming unconfirmed data.
5. Only clear pending after journal and index durability succeed. A failed local commit sets the operation error and leaves the journal available for restart.

Lookup has three outcomes: hit, miss, and I/O/corruption error. The error outcome must stop the walk; it may not be converted to a miss and silently resend or skip based on incomplete state. The module returns this tri-state through its public API so callers cannot accidentally ignore SQLite errors.

## Bounded memory

Use a fixed pending entry cap and byte cap, with the walk calling `flush` before either cap is exceeded. A checkpoint barrier is allowed only after the caller has flushed its queued metadata batch and small-file pack; otherwise the remote ACK would not cover entries that are about to be journaled. Keep one prepared lookup statement, one bounded insert batch, one parser buffer and the current `FsEntry`. Expose `confirmed_entries` as a SQL count/metric, not a retained map. Benchmark with SQLite cache explicitly configured and capture peak RSS.

## Alternatives rejected

- A sorted in-memory vector still has O(N) retained paths and does not solve restart memory.
- An mmap view violates the current no-mmap direction and does not bound address-space/page pressure for the requested scenario.
- Replacing the map with LMDB is not available on the current host with `MDB_VL32`; it is also a separate supply-chain task. SQLite is already a required dependency and supplies the needed disk B-tree.
- Pure append journal plus linear scan makes every path lookup O(N) and turns 1M recovery into an unacceptable throughput regression.

## Rollback and observability

Keep a format feature gate and legacy journal reader. Emit `checkpoint_recovery`, `checkpoint_replay`, `checkpoint_flush`, `checkpoint_migration`, and `checkpoint_failure` events with counts, bytes, replay offset and elapsed time, never paths or tokens. Tests must inject failures after remote ACK, after journal fsync, and during SQLite commit.

## Pre-Do audit decisions

- `tree_checkpoint.cpp` is linked into the common target so unit tests exercise the same implementation as `backupctl`; the public header exposes an opaque C-style handle and tri-state lookup rather than the storage container.
- The existing walk's 256-entry scan boundary is retained as the first pending bound, then an explicit entry/byte guard is added so future callers cannot grow pending without a barrier. The caller flushes metadata and pack queues before invoking the checkpoint flush.
- Sidecar migration uses a temporary database in the same directory, closes and fsyncs it, then renames it while the lock is held; the old journal is retained until replay metadata is durable.

## Performance hypothesis

The primary win is peak RSS and restart scalability, not necessarily single-entry lookup latency. Prepared SQLite lookups and bounded transactions should keep recovery throughput within a declared regression budget versus the legacy 100k baseline; if throughput regresses, batch transaction and page-cache evidence must identify the cause rather than reintroduce a full map.
