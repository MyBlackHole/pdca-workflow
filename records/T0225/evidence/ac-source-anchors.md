# 代码锚点（AC-2/AC-3/AC-4/AC-5 源码证据）

对象：percona-xtrabackup-8.0.25-17 `storage/innobase/xtrabackup/src/`

## A1 全表扫描比对页 LSN（AC-2）
- `write_filt.cc:52-54` — `xb_write_filt_t wf_incremental = {init, process, finalize, deinit}` 增量写过滤。
- `write_filt.cc:104-149` — `wf_incremental_process()`：逐页读 `FIL_PAGE_LSN`，`125-126` `else if (incremental_lsn > mach_read_from_8(page + FIL_PAGE_LSN)) continue;` 跳过未变页；`122-124` mysql.ibd 用 `metadata_from_lsn` 特判。
- `write_filt.cc:94,138,162,166` — delta 块魔数 `xtra`/`XTRA`、空槽 `0xFFFFFFFF`。
- `write_filt.cc:142-143` — 页号表写入 `delta_buf+npages*4`，页数据随后。
- `xtrabackup.cc:2907-2911` — `xtrabackup_copy_datafile()` 按 `xtrabackup_incremental` 选 `wf_incremental` else `wf_write_through`。
- `xtrabackup.cc:5393,5505-5572` — `xtrabackup_apply_delta()` 读 delta 块、解析页号、覆写目标页（含压缩 punched-hole 5557-5571）。

## A2 Changed Page Bitmap / page tracking（AC-3）
- `backup_mysql.cc:683-685` — 读取服务端 `innodb_track_changed_pages=ON`（仅 Percona Server）置 `have_changed_page_bitmaps=true`；否则恒 false→全扫描。
- `backup_mysql.cc:2179-2186` — `flush_changed_page_bitmaps()` 执行 `FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS`。
- `changed_page_bitmap.cc:567,588` — `xb_page_bitmap_init()` 构建 RB-tree+位图（区间 `incremental_lsn→checkpoint_lsn`）。
- `changed_page_bitmap.cc:836,885` — `xb_page_bitmap_range_init/get_next_bit()` 遍历置位页。
- `read_filt.cc:120-154` — `rf_bitmap_get_next_batch()` 用位图取变化页（142 置位真、154 清位界定块尾）。
- `xtrabackup.cc:4012-4024` — 无位图/`--incremental-force-scan` 时打印 "using the full scan" 回退全扫描。
- `changed_page_bitmap.cc:623-719` — 位图缺失区间打 warning 并返回 NULL→回退。

## A3 Redo Log Archiving（AC-4）
- `redo_log.cc:639-651` — `parse_archive_dirs()` 解析 `innodb_redo_log_archive_dirs`（`label:dir;`）。
- `redo_log.cc:653,700-736` — `Archived_Redo_Log_Monitor::thread_func()` 调 `innodb_redo_log_archive_start(label,subdir)` 启动归档。
- `redo_log.cc:1073-1105` — `copy_once()` 归档态从 `archived_log_monitor.get_reader()` 读归档 redo 写 xtrabackup_logfile。

## A4 增量 prepare（AC-5）
- `xtrabackup.cc:157,731-734,6580` — `--apply-log-only` 选项→`srv_apply_log_only`。
- `xtrabackup.cc:6535-6561` — `xtrabackup_apply_deltas()` 反序列化增量 Tablespace_map 并应用 delta。
- `xtrabackup.cc:2324-2340` — prepare 增量以 `incremental_to_lsn/last_lsn` 较大者作 `srv_start(false,to_lsn)` 起点。
- `xtrabackup.cc:7570-7585` — prepare + `--incremental-dir` 时 `xtrabackup_read_metadata()` 读增量 `xtrabackup_checkpoints`，赋 `incremental_lsn/to_lsn/last_lsn`。
- `xtrabackup.cc:6748` — prepare 后元数据标 `log-applied`（apply-log-only）或 `full-prepared`。
- **缺失确认**：`--rollback-only`、`--redo-lag`、`--page-tracking` 全仓无符号（已核验）。
- `xtrabackup.cc:403-404,1112-1133` — `--incremental-history-name/-uuid` 选项。
- `backup_mysql.cc:792-846` — `select_incremental_lsn_from_history()` 从 `PERCONA_SCHEMA.xtrabackup_history` 取 `innodb_to_lsn`。
- `xtrabackup.cc:2438-2452,4110-4123` — `xtrabackup_checkpoints` 写 `backup_type/from_lsn/to_lsn/last_lsn/flushed_lsn`。

核验日期：2026-08-07（.cc 内 grep 已实检，非子代理转述）。