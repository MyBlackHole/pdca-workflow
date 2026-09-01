---
schema: pdca.asset/v1
id: ontology:pitfall/backup-snapshot-race
type: pitfall
layer: Knowledge
status: active
summary: BackupHelper Snapshot 无超时与 m_sync_stat 竞态致提前 OnCopy 产出缺事件快照
relations:
  relates_to:
  - ontology:domain/backup
  specializes:
  - ontology:pitfall
---

# Backup Snapshot 无超时与竞态

**来源：** T0488 C-02，`fs-backup/fsdeamon/backup_helper.cpp:537-585`

**陷阱：** `DoSnapshot::Sync` 的 `while(true)` 以 `io_event_index <= m_sync_stat->io_event_index || timetamp_ns <=` 为成功条件，300s 才触发 `LogSwitch`，且 `m_sync_stat` 三线程无锁，`||` 可能提前退出致 `OnCopy` 拷贝未完全 replay 的 LMDB。

**后果：** 产出缺事件却标记成功的快照，`snapshot.db` 增量链需全量重建。

**纠正：** 加 5min 超时 + `m_down_mutex` 保护读 + 以 `log_file_index` 为主判定（`AND` 需内核语义确认）。
