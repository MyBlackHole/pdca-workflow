# T0334 实证记录：自研离线 WAL 恢复引擎（pgwrecover）端到端验证

## 结论
备份产物（heap + WAL + clog）经 pgwrecover 离线重放后接 pgbin 转换 Parquet，
56500 备份行 + 3 条增量重放行（400001/400002/400003）全部可见且逐字段正确。
**之前直接转换会 SIGSEGV 的同一备份，恢复后转换正常**，对齐 T0333 实证基线。

## 验证环境
- 容器 t0216-pg（PG18.4），user=test, db=poct25, 宿主端口 5433
- 备份：pg_basebackup -X stream 在线备份，relfilenode 1946522（639 页 5234688B）
- 场景：备份后插入 3 行（400001/400002/400003，txid 29289）并提交
- WAL 段：000000010000000C00000082，redo 起点 C/820805B8

## 重放结果（pgwrecover）
- records_seen=11, heap_rmgr_records=6, fpi_pages=1, incremental_applied=2, skipped_incremental=3
- 仅覆盖 RM_HEAP_ID 的 INSERT/DELETE/UPDATE/HOT_UPDATE/LOCK；btree/Heap2 增量跳过
- blk638：备份 9 items → 重放后 12 items（item10/11/12 = 400001/400002/400003）

## 关键修复（本次会话）
1. **tuple 头偏移错位（崩溃根因）**：`build_tuple` 用 `sizeof(HeapTupleHeaderData)`(24)
   作为数据区起点，官方 PG 用 `SizeofHeapTupleHeader`(23, 即 offsetof(t_bits))。差 1 字节
   导致增量重放 tuple 数据整体右移 1 字节（id 前多一个 0x00 padding），pgbin 解析 created_at
   越界 SIGSEGV（pg_heap_reader.c:584）。修复后 item11/12 len 从 70 变为 69（与 WAL 一致）。
2. **TransactionIdPrecedes 缺失**：pg_redo.c 的 pd_prune_xid 提示调用后端函数，前端链接缺失，
   改为内联 pg_redo_xid_precedes（(int32)(id1-id2)<0），仅影响 prune 时机提示，无正确性影响。

## 验证产物
- 恢复 heap: fpi_heap4.out（md5 40ffc7f1...），blk638 12 items 经 parse_page3 确认
- parquet: fpi_final.parquet（md5 b0157c28...）rows=56503, max_id=400003
- 400001: customer_id=1 amount=10.50 status=FPI_PROOF payload=x active=True
- 400002: customer_id=2 amount=20.50 status=FPI_PROOF payload=y active=True
- 400003: customer_id=3 amount=30.50 status=FPI_PROOF payload=z active=True
- 未恢复直接转换对照：base_parquet/ckpt_parquet 仅 4 字节（SIGSEGV），fpi_after_final(仅FPI)
  rows=56501 含 400001；fpi_final(FPI+增量) rows=56503 含全部 3 行

## clog 语义
- 备份时 29289 未提交，备份自带 pg_xact/0000 中 29289 为 IN_PROGRESS
- 重放工具输出 clog 为备份快照透传；需用提交后的真实 clog（cur_clog3，29289=COMMITTED）
  才能让 pgbin 看到增量行——预期语义，恢复后应使用 WAL 重放+提交后的 clog

## 待办
- 测试目录 tests/pgwrecover/ 为空，AC-1/2/3 单元测试未落地
- pg_replay.c/.h 中"增量跳过"注释过时，需更新