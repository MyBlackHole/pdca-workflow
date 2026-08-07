# XtraBackup 8.0.25 增量备份实现方案调研报告

- 任务：T0225（0807-xtrabackup-incremental-tech）
- 调研对象：`percona-xtrabackup-8.0.25-17`（标准 Percona XtraBackup 8.0.25 源码快照，非定制、非 git 仓）
- 日期：2026-08-07

## 调研目标

确立本项目**支持哪些 MySQL 增量备份实现方案**，逐项给出技术原理、触发参数、代码锚点与适用场景；并对照**第三方 / 其它业界方案**与**本项目缺失（未实现）**的增量能力，输出支持矩阵与差距分析。

## 方法

- **主证**：源码静态分析（对 `storage/innobase/xtrabackup/` 增量相关文件做行级追踪），锚点以 `file:line` 标注。
- **佐证**：Percona / MySQL 官方文档与发布说明（联网核实最新版本能力差异）。
- **口径**：区分「本项目（8.0.25）已实现」与「后续版本/第三方引入（本项目缺失）」两类。

## 发现

### 一、增量方案总览（支持矩阵）

物理/引擎级增量在备份阶段归根到底只有两种识别「变化页」的方式：**全表扫描比对页 LSN** 与 **服务端页跟踪位图**。本项目 8.0.25 两条都已具备（后条依赖 Percona Server）。

| 方案 | 引擎/机制 | 本项目(8.0.25) | 触发方式 | 依赖 |
|------|-----------|:---:|----------|------|
| 全表扫描比对页 LSN 增量（default） | InnoDB 页 | ✅ 已实现 | `--incremental(-basedir/-lsn)` | 无 |
| Changed-Page-Bitmap 加速增量 | Percona 页跟踪位图 | ✅ 已实现 | 同上 + Server 开启 `innodb_track_changed_pages=ON` | **Percona Server 8.0** |
| Redo Log Archiving（归档支撑） | MySQL 8.0 redo 归档 | ✅ 已实现 | `innodb_redo_log_archive_dirs` + 备份 | MySQL 8.0 架构 |
| 增量 prepare（delta 应用） | PXB | ✅ 已实现 | `--prepare --apply-log-only` + `--incremental-dir` | 基线全备 |
| 历史元数据增量起点 | PXB 历史表 | ✅ 已实现 | `--incremental-history-name/-uuid` | Percona Schema 历史表 |
| 官方 page tracking 页级增量 | MySQL 8.0.17+ | ❌ 缺失（8.0.27+） | `--page-tracking` | mysqlbackup 组件 |
| 并行 delta 合并 prepare | — | ❌ 缺失（8.4.0-3+） | `--prepare --parallel` | 新版本 |
| binlog / PITR 增量 | binlog | 🟢 互补 | `mysqlbinlog` 回放 | 逻辑级 |
| CDC（Canal/Debezium） | binlog | ❌ 非其职责 | — | 逻辑级/同步 |
| 存储/块级快照（ZFS/LVM/DRBD/云） | 存储层 | ❌ 非其职责 | — | 外部 |

> `🟢 互补`：XtraBackup 会复制 redo/binlog 供回放，但逻辑回放本身名称归属 binlog 工具链；`❌ 非其职责`：框架不解块级 /CDC 作业。

---

### 二、本项目已实现的增量方案

#### A1. 全表扫描比对页 LSN（默认主路径）

- **触发**：`--backup --incremental-basedir=<全量目录>` 或 `--incremental-lsn=<LSN>`；关闭位图时即纯全扫描。
- **原理**：备份时逐数据文件逐页读 `FIL_PAGE_LSN`，仅保留 `page_lsn > incremental_lsn` 的页写入增量；其余页直接跳过（write_filt.cc:125-126）。
- **调用链**：安装写过滤 `xtrabackup_copy_datafile()`（xtrabackup.cc:2907-2911）→ 增量态安装 `wf_incremental`（write_filt.cc:52-54）→ 逐页判 LSN 后写 delta。
- **delta 落盘格式**（write_filt.cc:94-174）：
  ```
  .delta 文件 = 若干 "delta 块"；每块含：
    头 4B 魔数  0x58745241 ("XTRA")  ↔  起始块 0x78747261 ("xtra")
    uint32[ ]  页号表       (delta_buf + npages*4)
    页字节流      Copy of changed pages (与页号表一一对应)
    0xFFFFFFFF   空槽结束标记 (finalize)
  配套 <name>.meta 元信息（page_size/space_id/space_flags, 由 xb_write_delta_metadata 写）
  ```
- **prepare 回写**：`xtrabackup_apply_delta()`（xtrabackup.cc:5393）读 delta 块、解析页号表并覆写目标页（5505-5572，含压缩页 punched-hole 5105-5571）。
- **开关**：`--incremental-force-scan` 强制忽略位图/页跟踪、走全扫描（xtrabackup.cc:884-888，4013-4018）。
- **局限**：全表扫描读全部页，变化页占比低时 IO 开销大。

#### A2 Changed-Page Bitmap（Percona Server 页跟踪优化）

- **触发与依赖**：仅当服务端变量 `innodb_track_changed_pages=ON`（Percona Server 8.0）才启用（backup_mysql.cc:683-685）；否则恒回退全扫描（标准 MySQL 无此变量）。
- **备份时**：`flush_changed_page_bitmaps()` 执行 `FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS`（backup_mysql.cc:2179-2186），把服务端「某 LSN 区间内的脏页位图」落盘为 `ib_modified_log_<seq>_<start_lsn>.xbm`。
- **xtrabackup 端**：构建 `xb_page_bitmap_init(from_lsn, checkpoint_lsn)` RB-tree+位图（changed_page_bitmap.cc:567,588）→ 遍历 `xb_page_bitmap_range_get_next_bit()` 定位置位页 → 只拷这些页（read_filt.cc:120-154，rf_bitmap）。
- **关键作用**：用服务端页位图直接定位「变化页」，绕开全表 LSN 逐页扫描，大表增量显著提速。
- **版本依赖**：Percona Server 8.0（XtraDB 在线日志位图；此算法 Per-8.0.27 起被官方 page tracking 取代，其在官方 PS 已废弃）。
- **局限**：无此变量则全扫描；位图区间缺失会打 warning 并回退全扫描（changed_page_bitmap.cc:623-719）。

#### A3 Redo Log Archive（redo 归档支撑机制）

- **触发**：服务端配置 `innodb_redo_log_archive_dirs`（`label:dir;`）；`Archived_Redo_Log_Monitor` 线程解析并启动（redo_log.cc:639-651,653）。
- **动作**：归档线程调用 `innodb_redo_log_archive_start(label, subdir)` 由服务端把 redo 持续写归档子目录（redo_log.cc:700-736）。
- **一致性意义**：备份期间 redo 可能被回收覆盖；归档使其可被继续读取，保证增量 prepare 的 redo 前滚不缺段。当主 redo 落后归档区时，`copy_once()` 切换为读归档（redo_log.cc:1073-1105,1034-1059）。
- **不依赖增量特有的**：全量/增量备份均可启用；增量 prerto 以该机制获取一致性 redo 位。

#### A4 增量 prepare（合并与还原链路）

- **`--apply-log-only`**：pre 加管理距离 `srv_apply_log_only`（xtrabackup.cc:6580），仅前滚 redo/合并 delta、**不**把数据页刷盘，以便继续叠加下一个增量；每层增量 prepare 后元数据写 `log-applied`（xtrabackup.cc:6748）。
- **delta 应用**：对所有增量目录，`xtrabackup_apply_deltas()`（xtrabackup.cc:6535-6561）→ 每个 delta 空间 `xtrabackup_apply_delta()` 按页号回写。
- **LSN 重定向**：prepare 增量时以 `incremental_to_lsn / incremental_last_lsn` 的较大值作为前滚起点（xtrabackup.cc:2324-2340）；恢复完成后校验 `log_get_lsn >= incremental_to_lsn`（6709-6721）。
- **checkpoint 读取：**`xtrabackup_read_metadata()` 从 deltas 目录 `xtrabackup_checkpoints` 读 `from_lsn/to_lsn/last_lsn/flushed_lsn`（xtrabackup.cc:7571-7583，其赋值在 7581-7583）。
- **还原收尾**：最后一次不带 `--apply-log-only` 的 prepare 执行 finalize（xtrabackup.cc:6787-6813）。
- **❗已移除项（在本版本缺失）**：`--rollback-only`、`--redo-lag` 在 8.0.25-17 中**无实现**（全仓无对应符号），已在 PRD 中被列为 A4 支持项、此为 Do 期修正为「缺失」。如需回滚未提交事务 / 限速合并，须依赖 `--apply-log` 内建崩溃恢复与运维限速而非这些开关。

#### A5 基于历史备份元数据

- **触发**：`--incremental-history-name` 或 `--incremental-history-uuid`（xtrabackup.cc:403-404,1112-1133）。
- **取 LSN**：`select_incremental_lsn_from_history()`（backup_mysql.cc:792-846）查询 `PERCONA_SCHEMA.xtrabackup_history` 取 `innodb_to_lsn`，按 name（798-808）或 uuid（811-822）；输出 `incremental_lsn`（836）作为本次增量起点。
- **建表/写入**：`insert_history_record` 及 `xtrabackup_history` 建表（backup_mysql.cc:1872-1926）。
- **意义**：免人工维护增量起始 LSN，按「最近一次历史备份」自动续作。

---

### 三、第三方 / 业界其它增量技术 与 本项目缺失项

> 口径：`XtraBackup 8.0.25 是否已提供`。

| # | 方案 | 8.0.25 | 差异/原理 | 备注(URL) |
|---|------|:---:|------|------|
| 1 | **官方 page tracking 页级增量**（`--page-tracking`） | ❌缺失 | MySQL 8.0.17+ 的 IO 层按 LSN 记录落盘页，服务端返回页 list；只拷变化页，免全扫。8.0.27 起支持；需 mysqlbackup 组件、单文件系统表空间；有 DDL bug(#106163) | docs.percona.com/percona-xtrabackup/8.0/page-tracking.html |
| 2 | **MySQL Enterprise Backup (MEB) 增量** | ❌(需 MEB) | `mysqlbackup --incremental=page-track|full-scan|optimistic`；page-track 用官方页跟踪+redo 前滚，optimistic 受堵自动退化 full-scan；商业 | dev.mysql.com/doc/mysql-enterprise-backup/8.4/en/mysqlbackup.incremental.html |
| 3 | **MEB optimistic / full-scan 变异** | ❌(需 MEB) | 与 XtraFullScan 思路相似，但三态+自动退化更健壮 | backup-incremental-options.html |
| 4 | **并行 delta 合并 prepare** | ❌(8.4.0-3+) | 增量 prepare 阶段并发应用 `.delta`，多表并行加速 | percona.com/percona-xtrabackup/8.4/release-notes/8.4.0-3.html |
| 5 | **binlog / PITR 逻辑增量** | 🟢互补 | 物理/逻辑全备 + `mysqlbinlog ... | mysql` 回放到事故点；秒级时间点，属逻辑回放 | refman/8.0/en/point-in-time-recovery-binlog.html |
| 6 | **mysqlbinlog --flashback / 闪回** | ❌ | 逆序 binlog 生成反操作；官方仅 bug#65178 补丁，云/发行版提供 | bugs.mysql.com/bug.php?id=65178 |
| 7 | **CDC 实时增量（Canal / Debezium）** | ❌(非其职责) | 订阅 binlog 出结构化变更流 + incremental snapshot；面向同步/重建，非恢复 | debezium.io connectors/mysql.html |
| 8 | **存储/块级快照 （ZFS `zfs send -i`、LVM thin、DRBD、云快照）** | ❌(非其职责) | COW 快照 O(1) + 快照间增量；需 flush 序，无 InnoDB 感知；块级 DRBD 双机镜像 | percona blog ZFS / LVM |

> 🟢`互补`：XBK 复制 redo（含归档）供回放，但回放本身靠 binlog 工具链。❌`非其职责`：块复制/DSC 不在物理备份工具边界内。

---

### 四、结论与建议

1. **本项目（8.1.25）实用增量能力 = 「全表扫描比对页 LSN」物理增量 + （Percona Server）changed-page bitmap 加速 + redo 归档保障 + —apply-log-only 增量合并 + history 续作**。这是可开箱即用的官方增量方案。
2. **最值得补齐的缺失特性 = 官方 page tracking（`--page-tracking`）**：自 8.0.27 起的核心能力，能显著降低增量 IO；本项目(8.0.25)尚需升级到 ≥8.0.27 才能获得。
3. 其他差距（并行 delta 合并、MEB 三态算法）为「版本/商业」差异，不影响 8.0.25 作为基础增量工具使用；`--rollback-only/--redo-lag` 在本版本已移除。
4. **与逻辑级（binlog/PITR）、CDC、块级快照互补而非冲突**：物理增量负责快速恢复，逻辑级负责秒级时间点，可按 RTO/RPO 组合选型。

## 参考资料

- 本项目源码：`storage/innobase/xtrabackup/src/`（write_filt / read_filt / changed_page_bitmap / redo_log / backup_mysql / xtrabackup）
- Percona 官方文档：page-tracking（https://docs.percona.com/percona-xtrabackup/8.0/page-tracking.html）；create-incremental-backup（.../8.0/create-incremental-backup.html）
- Percona 发布说明 8.4.0-3 / 8.4.0-6（docs.percona.com/percona-xtrabbackup/8.4/release-notes/...）
- MySQL 官方：PITR binlog（dev.mysql.com/doc/refman/8.0/en/point-in-time-recovery-binlog.html）；MEB incremental（dev.mysql.com/doc/mysql-enterprise-backup/8.4/en/mysqlbackup.incremental.html）；InnoDB Clone & page tracking 博客（dev.mysql.com/blog-archive/innodb-clone-and-page-tracking/）；bug#65178
- Percona blog：LVM for MySQL；ZFS-from-a-mysql-perspective
- Debezium MySQL connector（debezium.io/documentation/reference/stable/connectors/mysql.html）