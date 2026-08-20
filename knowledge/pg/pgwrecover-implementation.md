# 自研离线 WAL 恢复引擎（pgwrecover）— 实现要点

> 来源：T0334-0820-backup-recovery-engine（容器实证 PG18）
> 关系：T0333 `backup-recovery-wal-replay.md` 的下游——该篇解决"恢复机制调研与实证"，
> 本篇解决"自研恢复引擎的落地实现与踩坑"。

## 核心结论

**自研离线 WAL 恢复引擎（路径 B）可行**。不启动数据库，纯离线对备份产物
（heap + WAL + pg_control）重放 FPI + 增量记录，即可恢复出等价正常关闭快照，
接既有 pgbin 转换 Parquet。端到端实证：56500 备份行 + 3 条增量重放行全部可见且逐字段正确。

## 架构

```
pgwrecover <backup_dir> <out_heap> <out_clog> [--rel-oid=N]
 1. pg_control + backup_label → 恢复起点 LSN
 2. XLogReaderAllocate 打开 WAL（官方 xlogreader 前端化复用，pg_waldump 同款模式）
 3. 复制原始 heap 到 out_heap（未触达页与源一致），clog 透传
 4. 逐条 XLogRecord 分派：FPI 落页 + 增量重放（页 LSN 幂等跳过）
 5. 输出统计 JSON
```

## 关键实现要点

1. **官方 xlogreader 前端复用**：`XLogReaderRoutine` 提供 segment_open/segment_close/
   page_read 回调，page_read 内用 `WALRead` 读段。段缺失 = WAL 末尾（正常结束）。
   CRC 校验在 xlogreader 内部完成，失败经 errormsg 返回。

2. **起点定位**：`ControlFileData` 布局（8 字节对齐）：system_identifier@0,
   pg_control_version@8, catalog@12, state@16, time@20, checkPoint@28, checkPointCopy@36。
   `checkPointCopy.redo` 为默认起点；backup_label 的 `START WAL LOCATION` 覆盖（在线备份必须）。

3. **FPI 落页**：`XLogRecHasBlockImage` 识别 FPI → `RestoreBlockImage` 还原（含解压）→
   按 blknum*BLCKSZ 偏移 pwrite 整页。幂等：目标页 `pd_lsn >= 记录 LSN` 则跳过。

4. **增量重放**：无 FPI 的 heap 增量块 → `build_tuple` 重建 tuple 落页。
   仅处理 RM_HEAP_ID 的 INSERT/DELETE/UPDATE/HOT_UPDATE/LOCK；btree/Heap2 增量跳过
   （备份 FPI 已覆盖所需页）。

5. **clog 语义**：备份时未提交事务的 clog 状态为 IN_PROGRESS，重放输出为备份快照透传。
   要看到增量提交行，需用提交后的真实 clog（或 WAL 重放+提交后的 clog）给 pgbin。

## 踩坑记录（重要）

1. **tuple 头偏移错位（崩溃根因）**：`build_tuple` 重建 tuple 时，数据区起点必须用
   `SizeofHeapTupleHeader`（=23，即 `offsetof(HeapTupleHeaderData, t_bits)`），
   **不是** `sizeof(HeapTupleHeaderData)`（=24）。差 1 字节导致增量 tuple 数据整体右移
   1 字节（id 前多一个 0x00），pgbin 解析后续字段越界 SIGSEGV（pg_heap_reader.c:584）。
   症状：增量行 len 多 1（70 vs 69），id 从 0x061A82 变 0x061A8200。

2. **TransactionIdPrecedes 缺失**：`pd_prune_xid` 提示调后端函数，前端链接缺失。
   内联实现 `(int32)(id1-id2) < 0`（XID 回卷语义），仅影响 prune 时机提示，无正确性影响。

3. **ItemIdData 位域（PG18）**：`unsigned lp_off:15, lp_flags:2, lp_len:15`（32-bit 字）。
   解析：off = v & 0x7FFF, fl = (v>>15)&3, ln = (v>>17)&0x7FFF。用 16-bit lp_off 的旧工具
   会解析出错误偏移（off=40872 之类），导致误判页损坏。

4. **调试陷阱**：调试二进制必须用当前源码重编译（旧 .o 会指向过期路径/旧行号，误导定位）。

## 复用资产

- `third_party/pg184/src/xlogreader.c`：官方 WAL 读取器（前端可链接）
- `third_party/pg184/include/`：WAL/clog/heap 头文件
- `knowledge/pg/backup-recovery-wal-replay.md`：T0333 恢复机制调研

## 待推进

- MySQL 恢复引擎（T0333 决策：自研，undo 回滚 + trx_sys + purge 四要素）
- 更多 rmgr（gin/gist/spgist）重放、PITR、wal_level=minimal 场景