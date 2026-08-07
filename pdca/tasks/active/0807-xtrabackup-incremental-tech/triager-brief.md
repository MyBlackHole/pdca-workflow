# Triager Brief — T0225 XtraBackup 增量技术调研

## 分类

- category: `enhancement`
- scenario_type: `research`
- 触发：用户要求「走 PDCA 流程分析本项目支持哪些 MySQL 增量实现技术」

## 验证结果（claim verification）

对工作目录 `percona-xtrabackup-8.0.25-17` 源码进行静态核查，确认项目内含真实增量实现，证据如下：

| 技术 | 关键证据 | 文件 |
|------|---------|------|
| LSN 页级对比增量 | `wf_incremental_*`：`incremental_lsn > FIL_PAGE_LSN` 跳过，「XTRA」delta 块 + 页号表 | storage/innobase/xtrabackup/src/write_filt.cc:104-174 |
| 增量写过滤分派 (`wf_incremental`/`wf_write_through`) | `xb_write_filt_t wf_incremental = {...}` 含 init/process/finalize/deinit | write_filt.cc:52-54 |
| Changed Page Bitmap（脏页位图/page tracking） | `FLUSH CHANGED_PAGE_BITMAPS`、`ib_modified_log_*.xbm`、RB-tree+位图块 4096B 结构 | src/changed_page_bitmap.cc:567; src/backup_mysql.cc:685-744,2179 |
| Redo Log Archiving（redo 归档） | `innodb_redo_log_archive_dirs`、`Archived_Redo_Log_Monitor` | src/redo_log.cc:573-731 |
| 参数面 | `--incremental`/`--incremental-lsn`/`--incremental-basedir`/`--incremental-dir`/`--incremental-force-scan`/`--incremental-history-name/uuid` | src/xtrabackup.cc:166-404,764-1133 |

结论：claim 成立，值得产出系统性技术调研。

## 信息缺口

- 每类技术的**增量 prepare（--apply-log-only / delta 合并 / redo apply）链路细节**待深入代码确认。
- `FLUSH CHANGED_PAGE_BITMAPS` 对 Server 版本的依赖（Percona Server 8.0 才有）待确认。
- 产出物（报告）的存放路径/格式未定（需用户决策，见 P1-1）。

## 去重

- 全量检索 `pdca/tasks/{active,archive}` 与 `knowledge/`，无与本任务重复的 XtraBackup/增量备份调研任务。
- 相关归档任务均为 PG/Parquet/NBU 方向，与本任务无交集。

## 建议下一步

1. P1 澄清产出物位置/形式（一个决策问题）。
2. P2 确认调研覆盖面（增量写 + 增量 prepare + 归档 + page tracking + 版本依赖）。
3. P3 合成完整 PRD → P6 终审 → Do 执行。

## 日期

2026-08-07