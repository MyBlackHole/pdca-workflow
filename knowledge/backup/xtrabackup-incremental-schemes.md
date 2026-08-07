# XtraBackup 8.0 系列增量备份方案速览（通用知识）

来源：任务 T0225 调研。对象：Percona XtraBackup 8.0.25（主要物理增量基准）。

## 物理增量两条路线

引擎级物理增量在备份阶段识别「变化页」只有两种方式：

1. **全表扫描比对页 LSN（full-scan）**
   - 逐页读 `FIL_PAGE_LSN`，只拷 `page_lsn > incremental_lsn` 的页。
   - 兜底方案、无版本依赖；变化页占比低时存在全读 IO 开销。
   - anchor：`write_filt.cc:125-126`、`xtrabackup.cc:2907-2911`。
2. **服务端页跟踪（page tracking）位图**
   - XtraBackup 8.0.25 用的是 **Percona Server changed-page bitmap**（`innodb_track_changed_pages=ON`，`ib_modified_log_*.xbm` 位图）；8.0.27+ 改用 **MySQL 8.0.17+ 官方 page tracking**（`--page-tracking`，消费 mysqlbackup 组件返回的页清单）。
   - 只拷位图置位页，大表提速明显；依赖服务端能力，未启用则自动回退全扫描。

## 增量参数族

- `--incremental` / `--incremental-basedir` / `--incremental-lsn`：增量起点指定。
- `--incremental-force-scan`：强制跳过位图/页跟踪做全扫描。
- `--incremental-dir`：prepare 时指定增量目录；读其 `xtrabackup_checkpoints` 的 from_lsn/to_lsn。
- `--apply-log-only`：增量 prepare 只前滚 redo+合并 delta，不刷数据页，供连续叠加。
- `--incremental-history-name/-uuid`：从 `PERCONA_SCHEMA.xtrabackup_history` 自动取上次备份 to_lsn 作为起点。

## 版本边界（易踩坑）

- 8.0.25：**无**`--page-tracking`（8.0.27 才有）；`--rollback-only`、`--redo-lag` 已移除。
- 8.0.30：移除 Percona changed-page 算法，只留 full-scan + 官方 page tracking。
- 8.4.0-3+：增量 prepare 支持并行合并 `.delta`（`--prepare --parallel`）。
- 官方 page tracking 需：mysqlbackup 组件、单文件系统表空间；存在 DDL bug #106163。

## 与其它方案的互补

- binlog/PITR、CDC(Canal/Debezium)、块级快照（ZFS/LVM/DRBD/云）均与 XtraBackup 物理增量互补而非替代。

## 参考

## MariaDB 插件真增量（10.1/XtraDB）

- MariaDB 10.1（XtraDB）**确曾有插件式真增量**：
  - `INFORMATION_SCHEMA.CHANGED_PAGE_BITMAPS` 插件（MYSQL_INFORMATION_SCHEMA_PLUGIN，MDEV-17122/commit b7ff5f1），承载 `FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS`。
  - `INNODB_CHANGED_PAGES` 表（SPACE_ID/PAGE_ID/START_LSN/END_LSN），由 log-tracking 线程解析 redo 更新。
  - 服务端变量 `innodb_track_changed_pages`；mariabackup 10.1 据此只读位图页、免全扫描真增量。
- 该插件仅存于 XtraDB（10.1）：10.2+ 换 InnoDB 后废弃——`innodb_track_changed_pages` 10.2.6 起 ignored、mariabackup 移除 bitmap（MDEV-18985）、2024 commit 92f87f2 删除代码；重实现请求 MDEV-10137 未落地。
- 结论：真增量共三条路线 = Percona Server(bitmap)、MySQL 8.0.27+(page-tracking)、**MariaDB 10.1/XtraDB(CHANGED_PAGE_BITMAPS 插件, 已 EOL)**。现行 MariaDB 10.2~11 无真增量，仅 LSN 全扫描。

- docs.percona.com/percona-xtrabackup/8.0/page-tracking.html、create-incremental-backup.html
- dev.mysql.com/doc/mysql-enterprise-backup/8.4/en/mysqlbackup.incremental.html
- dev.mysql.com/blog-archive/innodb-clone-and-page-tracking/

_正式登记见 records/<T0225>/experience（Act 阶段）_