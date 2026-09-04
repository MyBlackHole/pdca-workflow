---
schema: pdca.asset/v1
id: ontology:domain/pg-backup-recovery-wal-replay
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pg-backup-recovery-wal-replay/1.0.0
summary: PG 在线备份 → WAL 恢复一致性 — 机制要点
domain:
- ontology:domain/pg
relations:
  specializes:
  - ontology:domain/pg
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# PG 在线备份 → WAL 恢复一致性 — 机制要点

> 来源：T0333-0820-backup-log-recovery（容器实证 PG18）
> 关系：T0325 `pg/visibility-clog-infomask.md` 的上游——该篇解决"正常关闭快照可见性"，
> 本篇解决"非正常关闭备份如何恢复到等价正常关闭快照"。

## 核心结论

**PG 恢复 = 仅 WAL 重放，无独立 undo/回滚步骤**。MVCC 元组（xmin/xmax）+ clog 天然标记
aborted → 未提交行不可见。这是 PG 恢复复杂度低于 MySQL 一个量级的根本原因。

## 恢复流程（在线备份场景）

1. **起点定位**：`pg_control`（`ControlFileData.checkPoint.redo`）+ 在线备份的
   `backup_label`（`START WAL LOCATION` 覆盖默认起点，保证从备份点完整重放）。
   实证：`starting backup recovery with redo LSN C/7F000028, checkpoint LSN C/7F79F280`。
2. **前滚**：WAL `XLogRecord` 逐条分派 `rm_redo`（`XLOG_HEAP*` / `XLOG_BTREE*`）。
   每条含 FPI（full-page image）或增量；页头 LSN（`pd_lsn`）< record LSN 才应用（幂等跳过）。
   参考源码：`xlogrecovery.c`（`RedoRecovery`）、`heapam_xlog.c`、`nbtxlog.c`。
3. **完成标志**：`completed backup recovery ... end LSN ... consistent recovery state reached`
   ——重放至一致态后即等价正常关闭快照，可直接停库提取 heap + pg_xact。
4. **clog 天然正确**：重放后 clog 已含全部提交/中止位；pgbin 按 clog 判定即可，无需物理回滚。

## 在线备份恢复点语义（实证）

- `pg_basebackup -X stream` 的恢复点 ≈ **备份开始时的已提交快照** + 后续已提交 WAL。
- 备份期间提交的事务是否纳入，取决于其 commit 记录是否落在备份捕获的 WAL 范围内：
  - 活跃事务（备份开始时未提交）若其 commit 在备份 WAL 之后 → **不纳入**（恢复点=备份开始快照）。
  - 若提交记录已含于备份 WAL → 纳入。
- 实证：活跃事务插入 5000 行未提交 → 备份恢复后不见；后续提交的 500 行 → 恢复后可见。

## 未恢复直接转换的后果（实证）

备份产物 heap **不应用 WAL 直接 pgbin** → SIGSEGV 段错误（UBSAN：numeric 解码
`signed integer overflow`，`pg_heap_reader.c:151`）。heap 页含未刷盘/不一致数据被当数值解码。
**必须经日志恢复到一致态才能物理直读转换。**

## 边界

- 需 `wal_level` 支持 FPI（`minimal` 级别无 FPI 增量场景重放可能失败）；pg_basebackup 全量
  含所有页，无此问题。
- 恢复后须同快照携带 heap + pg_xact（只拷 heap 不拷 clog 会误判全 invisible，T0325 已知）。
- 物理直读仅需 heap+btree 的 REDO，其余 rmgr（gin/gist/spgist/seq/logical）可跳过。