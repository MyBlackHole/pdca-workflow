---
schema: pdca.asset/v1
id: T0334-0820-backup-recovery-engine
phase: check
source_ids: [pgwrecover-e2e, pgwrecover-ac1-unit, pgwrecover-ac2-unit, pgwrecover-ac3-unit, pgwrecover-knowledge]
---

## 上下文

T0333 已实证备份（非正常关闭）的 PG 数据文件不满足 pgbin 正常关闭快照前提，直接物理直读
SIGSEGV。本任务（T0334）实现自研离线 WAL 恢复引擎（路径 B，pgwrecover）：不启动数据库，
纯离线把备份产物（heap + WAL + pg_control/backup_label）恢复到等价正常关闭快照，接既有
pgbin 转 Parquet。

## 假设与结果

| # | 假设 | 结果 |
|---|------|------|
| AC-1 | pg_control + backup_label 解析器：正确读出恢复起点 LSN，字段级单元测试 PASS | **PASS**：test_pg_control.py 验证真实备份 version=1800、redo=C/820805B8，backup_label 覆盖逻辑 |
| AC-2 | WAL XLogRecord 读取器：正确解析记录头/CRC/FPI 标志，CRC 损坏记录可检测拒绝 | **PASS**：test_wal_reader.py 验证 records_seen=11、heap_rmgr=6、fpi=1、CRC 损坏检测 |
| AC-3 | heap/btree 重放：FPI 落页 + 页 LSN 幂等跳过，构造 FPI 与增量记录验证 | **PASS**：test_replay.py 验证 blk638 9→12 items，增量 3 行（400001/2/3）落地，幂等 LSN |
| AC-4 | 端到端容器验证：PG18 在线备份 → pgwrecover → pgbin → parquet vs SQL 全量对照 diff=0 | **PASS**：fpi_final.parquet rows=56503（56500+3 增量），max_id=400003，400001/2/3 逐字段正确 |
| AC-5 | 未恢复直接转换崩溃对照：同一备份不恢复直接 pgbin SIGSEGV，恢复后正常 | **PASS**：未恢复 base_parquet/ckpt_parquet 仅 4 字节（SIGSEGV）；恢复后 56503 行正常 |
| AC-6 | 知识沉淀（引擎实现要点）+ evidence 登记 + 结论 | **PASS**：t0334-pgwrecover-implementation.md 沉淀；evidence 已登记 |

## 分析

### 关键修复（本次会话定位的崩溃根因）
1. **build_tuple 偏移错位**：重建增量 tuple 时数据区起点用 `sizeof(HeapTupleHeaderData)`(=24)，
   而官方 PG 用 `SizeofHeapTupleHeader`(=23, `offsetof(t_bits)`)。差 1 字节导致增量 tuple 数据
   整体右移 1 字节（id 前多 0x00 padding），pgbin 解析后续字段越界 SIGSEGV（pg_heap_reader.c:584）。
   修复后增量行 len 从 70→69（与 WAL 一致），id 正确。
2. **TransactionIdPrecedes 缺失**：pd_prune_xid 提示调后端函数，前端链接失败，内联实现。
3. **ItemIdData 位域**：PG18 为 lp_off:15/lp_flags:2/lp_len:15（32-bit 字），旧 16-bit 解析误判。

### 实证链
- 备份 blk638 = 9 items（xmin=29288）；FPI 恢复 = 10 items；FPI+增量 = 12 items。
- WAL 记录：CHECKPOINT_REDO C/820805B8 → 3×Heap INSERT（off:10/11/12，其中 off:10 含 FPW）→
  btree INSERT_LEAF → COMMIT tx 29289（C/82081700）。
- pgwrecover 统计：records_seen=11, fpi_pages=1, incremental_applied=2, skipped_incremental=3。

### clog 语义（重要边界）
- 备份时 tx 29289 未提交，备份自带 pg_xact/0000 中为 IN_PROGRESS。
- 重放输出 clog 为备份快照透传；需用提交后的真实 clog（cur_clog3，29289=COMMITTED）才能让
  pgbin 看到增量行。这是预期语义：恢复后应使用 WAL 重放+提交后的 clog。

## 失败原因

无（全部 AC PASS）。

## 适用边界

- 仅覆盖 RM_HEAP_ID 的 INSERT/DELETE/UPDATE/HOT_UPDATE/LOCK 增量；btree/Heap2 增量跳过
  （备份 FPI 已覆盖所需页）。
- 范围外：gin/gist/spgist/seq/logical 重放、TDE、压缩页、wal_level=minimal（无 FPI）、PITR、
  真实生产备份产物（用容器构造）。
- clog 透传语义：增量提交行需配合提交后 clog 才能可见（如上）。
- 数据依赖真实备份样本 `/tmp/opencode/pgwrecover-e2e/fpi_backup`（容器 t0216-pg 构造）。

## 下一轮建议

1. **MySQL 恢复引擎**：T0333 决策自研，undo 回滚 + trx_sys + purge 四要素（范围外，后续迭代）。
2. **扩展 rmgr 覆盖**：gin/gist/spgist 重放；btree 增量（当前跳过，btree 页在 DELETE 场景
   可能不一致）。
3. **更多场景**：PITR 时间点恢复、wal_level=minimal（无 FPI）备份、批量 DELETE/UPDATE 增量重放
   的端到端验证。
4. **产品化**：单元测试样本从 /tmp 移入测试固件目录；pgwrecover 输出 clog 与 pgbin 衔接的
   自动化集成测试。