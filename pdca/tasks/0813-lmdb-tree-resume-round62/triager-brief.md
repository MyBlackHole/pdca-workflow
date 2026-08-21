# Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- priority: P0
- source: production-level objective for incremental backup and massive-file resume

## 事实核验

- `src/metadata_store.cpp` already contains an optional LMDB backend and `auto` selects it when compiled, but the normal integration suite assumes the cache is SQLite and fails against an LMDB-default binary with `file is not a database`.
- `tests/benchmark_metadata_index.sh` can run both backends; one 20,000-entry probe measured unchanged scan at `0.0667s` LMDB versus `0.0741s` SQLite, but this is one unpaired sample and is not production evidence.
- `--incremental-local` persists metadata only after `TREE_END`; the source walk and transfer have no durable per-batch checkpoint contract that can be validated after process interruption.
- Existing resume coverage proves large regular-file partial PUT/GET resume, not a massive recursive TREE interrupted after confirmed batches.

## 查重

- T0247 covered small-file pack streaming decode and did not add metadata checkpoint state or TREE transfer recovery.
- Existing metadata tasks cover the local SQLite/LMDB abstraction and generation correctness, but no active or archived task covers a resumable TREE checkpoint protocol.

## 推荐方向

1. Make LMDB a first-class tested backend: run the same integration, corruption, rollback and paired benchmark matrix against LMDB and SQLite, with no implicit cache-format assumptions.
2. Add an optional capability-negotiated TREE checkpoint ledger. A server checkpoint is acknowledged only after the corresponding bounded batch is applied; the client binds each checkpoint to source metadata fingerprints and remote generation.
3. On restart, replay only unconfirmed or source-mutated entries. Invalid, stale, incompatible or corrupted checkpoints fall back to the existing safe full replay; old peers remain compatible through capability negotiation.

## 当前需要用户决策

- checkpoint 的安全边界：推荐“逐批确认 + 每项 fingerprint 校验”，不推荐仅按路径游标盲跳。
- backend 默认：推荐 `auto` 在编译含 LMDB 时继续选择 LMDB，显式 `sqlite` 保留回退，不做静默格式转换。
- 兼容策略：推荐新 capability 可选，旧 peer 无 checkpoint 时走现有路径，不修改旧 peer 的既有语义。
