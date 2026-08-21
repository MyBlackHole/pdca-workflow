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

## T0336 扩展（MULTI_INSERT / UPDATE prefix-suffix / btree 决策）

> 来源：T0336-0820-pgwrecover-incremental-scope。证据：`t0336-btree-skip-justification.md`、
> 样本 `/tmp/opencode/t0336-*`、单测 `tests/pgwrecover/test_redo_scope.py`（9 项全 PASS）。

### 1. XLOG_HEAP2_MULTI_INSERT 重放（S1）

- **分发掩码**：`info & XLOG_HEAP_OPMASK`（0x70）。T0334 用 `&~0x70` 使 UPDATE(0x20)
  误路由进 redo_heap_insert（报 `INSERT blk 2 off`），已修。
- **不可复用 build_tuple**：`xl_multi_insert_tuple` 头 7 字节（ntuples 后追加 offnum），
  而 `xl_heap_header` 为 5 字节。复用 build_tuple 会让 tuple 数据错位 2 字节。
  按官方布局直接构造 HeapTupleHeader（含 bitmap 对齐）。

### 2. XLOG_HEAP_UPDATE prefix/suffix 重组（S2）

对齐官方 `heapam_xlog.c`（PG18 843-904 行）：
- flags 含 `XLH_UPDATE_PREFIX_FROM_OLD`(0x20) → 先读 uint16 prefixlen；
  含 `XLH_UPDATE_SUFFIX_FROM_OLD`(0x40) → 读 uint16 suffixlen（WAL 内先后缀后前缀）；
  再读 `xl_heap_header`，tuplen = 剩余字节。
- 重组 = WAL 内 bitmap/padding(xlh.t_hoff-23) + 旧 tuple 前缀(t_hoff 起 prefixlen 字节)
  + WAL 中间数据 + 旧 tuple 末尾后缀(oldtlen-suffixlen 起)；newlen=23+tuplen+prefixlen+suffixlen；
  设置 xmin/cmin/xmax/ctid/infomask2/infomask/t_hoff，含边界检查。
- **TOAST 影响**：文本超阈值被 TOAST（外联指针不参与前后缀比较），PG 只压定长列
  （prefixlen=4）；内联文本才触发 0x60（PREFIX|SUFFIX）。

### 3. 同页 UPDATE 分支 bug（踩坑）

同一页内 UPDATE（oldblk==newblk，如 HOT 更新）原实现修改 opage 却写回 npage，
导致**旧版本元数据修改丢失**（重放 item0 保持备份原样：xmax=22、ctid=(0,1)，
而运行库为 xmax=0、ctid=(0,2)）。修复：同页分支直接操作 npage；跨页分支分别写回。

### 4. 页对比测试的 hint bit 语义

运行库读取 tuple 时按 clog 动态标记 `HEAP_XMIN_COMMITTED`(0x100)/
`HEAP_XMAX_COMMITTED`(0x400) 并写回，备份/重放不设置（可见性靠 clog 判断）。
页对比测试需屏蔽这两个位 + `HEAP_XMAX_INVALID`(0x800) 时的 xmax 残留值。
此外运行库后续 VACUUM prune 会标记 DEAD item，不在增量 WAL 内，
场景对比只验证增量新页（blk2）。

### 5. btree 决策（S3b，见独立文档）

btree 无 FPI 的增量块跳过；FPI 仍落页。因 pgbin 不读索引 fork，
跳过不影响 heap→parquet 正确性，btree 一致性列为后续独立任务。

## 待推进

- MySQL 恢复引擎（T0333 决策：自研，undo 回滚 + trx_sys + purge 四要素）
- 更多 rmgr（gin/gist/spgist）重放、PITR、wal_level=minimal 场景