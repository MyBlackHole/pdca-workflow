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
| 历史元数据增量起点 | PXB 历史表 | ✅ 已实现 | `--incremental-history-name/-uuid` | Percona Schema 历史表 |
| 官方 page tracking 页级增量 | MySQL 8.0.17+ | ❌ 缺失（8.0.27+） | `--page-tracking` | mysqlbackup 组件 |

> **🅰️ 口径澄清（重要）**：若以「**真增量 = 免全表扫描、只读变化页**（page tracking / bitmap）」为界，剔除「LSN 全表扫描」后：本项目 8.0.25 的**真增量仅支持 Percona Server**（changed-page bitmap）；官方 MySQL 与 MariaDB(10.2+) 在 8.0.25 上**没有真增量**——官方 MySQL 需升级 8.0.27+ 用官方 page-tracking，MariaDB 始终只能用 LSN 全扫描（无官方 page tracking、无 bitmap）。本报告其余部分同时保留「LSN 全扫描增量」作为基础能力口径；两档均已在支持矩阵中标注。

---

### 一.5 增量技术总表（MySQL 家族）

> 汇总表：技术 → 家族 → 起始版本 → 触发 → 真增量口径 → PXB 8.0.25 支持。

| # | 增量技术 | 归属家族 | 起始版本 | 触发方式 | 真增量(免全扫) | PXB 8.0.25 |
|---|---------|:---:|---|---|---|:---:|
| 1 | **LSN 全表扫描物理增量** | MySQL / MariaDB / Percona | 任意 | `--incremental(-basedir/-lsn)` | ❌（全扫描） | ✅ 已实现 |
| 2 | **Changed-Page-Bitmap（XtraDB 位图）** | Percona Server | PS 5.5.27 | Server `innodb_track_changed_pages=ON` + `--incremental` | ✅ | ✅ 已实现 |
| 3 | **Changed-Page-Bitmap（XtraDB 位图）** | MariaDB 10.0/10.1 | 10.1（FLUSH 10.1.6） | `innodb_track_changed_pages` + mariabackup 10.1 | ✅ | ❌（10.2+ 已移除） |
| 4 | **官方 page tracking（引擎位图）** | MySQL | 8.0.17 | —（引擎内部，Clone 引入） | ✅ | ❌（引擎在，PXB 端 8.0.27+） |
| 5 | **MEB 消费官方 page tracking** | MySQL（商业） | MEB 8.0.18 | `mysqlbackup --incremental=page-track` | ✅ | ❌（需 MEB） |
| 6 | **PXB 消费官方 page tracking** | MySQL / Percona | PXB 8.0.27 | `--page-tracking` | ✅ | ❌（8.0.25 缺失） |
| 7 | **历史元数据续作（增量起点选取）** | PXB | 8.0（全系） | `--incremental-history-name/-uuid` | —（增量起点） | ✅ 已实现 |

> 真增量口径=免全表扫描、只读变化页。增量 prepare / 并行 delta 合并 / binlog 逻辑 / flashback 均属**还原或逻辑级**阶段，不计入本总表；历史元数据为增量起点选取辅助项。

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
- **开关**：`--incremental-force-scan` 强制忽略位图/页跟踪、走全扫描（xtrabackup.cc:884-888，4013-4018）。
- **局限**：全表扫描读全部页，变化页占比低时 IO 开销大。

#### A2 Changed-Page Bitmap（Percona Server 页跟踪优化）

- **触发与依赖**：仅当服务端变量 `innodb_track_changed_pages=ON`（Percona Server 8.0）才启用（backup_mysql.cc:683-685）；否则恒回退全扫描（标准 MySQL 无此变量）。
- **备份时**：`flush_changed_page_bitmaps()` 执行 `FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS`（backup_mysql.cc:2179-2186），把服务端「某 LSN 区间内的脏页位图」落盘为 `ib_modified_log_<seq>_<start_lsn>.xbm`。
- **xtrabackup 端**：构建 `xb_page_bitmap_init(checkpoint_lsn_start)` RB-tree+位图（changed_page_bitmap.cc:567，区间起点取全局 `incremental_lsn`）→ 遍历 `xb_page_bitmap_range_get_next_bit()` 定位置位页 → 只拷这些页（read_filt.cc:120-154，rf_bitmap）。
- **关键作用**：用服务端页位图直接定位「变化页」，绕开全表 LSN 逐页扫描，大表增量显著提速。
- **版本依赖**：Percona Server 8.0（XtraDB 在线日志位图；此算法 Per-8.0.27 起被官方 page tracking 取代，其在官方 PS 已废弃）。
- **局限**：无此变量则全扫描；位图区间缺失会打 warning 并回退全扫描（changed_page_bitmap.cc:623-719）。

#### A3 基于历史备份元数据

- **触发**：`--incremental-history-name` 或 `--incremental-history-uuid`（xtrabackup.cc:403-404,1112-1133）。
- **取 LSN**：`select_incremental_lsn_from_history()`（backup_mysql.cc:792-846）查询 `PERCONA_SCHEMA.xtrabackup_history` 取 `innodb_to_lsn`，按 name（798-808）或 uuid（811-822）；输出 `incremental_lsn`（836）作为本次增量起点。
- **建表/写入**：`insert_history_record` 及 `xtrabackup_history` 建表（backup_mysql.cc:1872-1926）。
- **意义**：免人工维护增量起始 LSN，按「最近一次历史备份」自动续作。

---

### 二.5 MySQL 与 MariaDB 增量方案对照（含 changed-page-bitmap 边界澄清）

| 增量方案 | MySQL（官方） | MariaDB（10.2+） |
|---------|:---:|:---:|
| LSN 全表扫描物理增量（PXB / mariadb-backup `--incremental`） | ✅ | ✅（10.2+ 默认且唯一） |
| Changed-Page-Bitmap 位图加速 | ❌（仅 Percona Server 专有） | ❌（仅 10.1/XtraDB 支持，10.2+ 移除） |
| 官方 page tracking（MySQL 8.0.17+，`--page-tracking`） | ⚠️ 仅 MEB 或 PXB≥8.0.27 | ❌ |

**关键澄清**：
- Changed-Page-Bitmap 源自 **XtraDB（Percona）**：Percona Server 全系、MariaDB 10.1（XtraDB 时代）支持；官方 MySQL 从未支持（无 `innodb_track_changed_pages` 变量，代码见 backup_mysql.cc:683-685 → 恒 false → 回退全扫描）。Percona Server 于 **5.5.27** 首引入 XtraDB changed page tracking（配合 `INNODB_CHANGED_PAGES`），5.6/5.7/8.0 沿续。
- MariaDB 10.2 起用 InnoDB，该特性被移除：`innodb_track_changed_pages` 于 10.2.6 起 deprecated/ignored，mariabackup 10.2 移除 bitmap 支持（MDEV-18985），2024-02 commit 92f87f2 彻底删除（`extra/mariabackup/changed_page_bitmap.cc` 移除 1043 行）。
- 官方 page tracking 是 MySQL 8.0.17+ InnoDB Clone 引入的引擎内部机制，仅通过 `mysql_page_track` 组件服务供 MEB（及 PXB≥8.0.27）消费；MySQL/MariaDB 均无面向用户的增量备份内置命令。

### 各家族「增量技术 × 起始版本」对照矩阵

| 服务器家族 | 增量技术 | 起始版本 | 消费工具 | 现状 |
|:---:|---|---|---|---|
| **MySQL（官方）** | LSN 全扫描增量 | 任意 | PXB / MEB | 通用兜底，无版本依赖 |
| | 官方 page tracking（engine） | **8.0.17** | — | 随 InnoDB Clone 引入引擎位图跟踪（WL #10223） |
| | MEB 消费 page tracking（`--incremental=page-track`，默认） | **8.0.18** | MEB | 8.0.18 起默认，此前默认 full-scan |
| | PXB 消费官方 page tracking（`--page-tracking`） | **8.0.27** | PXB ≥ 8.0.27 | MDB 改造后 PXB 改用官方页跟踪 |
| **MariaDB** | LSN 全扫描增量 | 10.1 / 10.2+ | mariabackup `--incremental` | 10.2+ 默认且唯一 |
| | changed-page 位图（XtraDB） | **10.0/10.1（XtraDB）** | mariabackup 10.1 | `innodb_track_changed_pages`；`FLUSH CHANGED_PAGE_BITMAPS` 于 10.1.6 起 | 
| | 位图移除，仅 LSN | 10.2+ | mariabackup | XtraDB → InnoDB；10.2.6 起`ignored`；2024 删代码 |
| **Percona Server** | XtraDB changed page 位图 | **5.5.27（-29.0）** | PXB "真增量" | 免全扫；`innodb_track_changed_pages` + `INNODB_CHANGED_PAGES`；5.6.11-60.3 稳定 |
| | （8.0.30+ 倾向官方 page tracking） | 8.0.30 | PXB | Per-8.0 位图算法 deprecated，官方 track 接管 |

> 版本依据：MDEV-18985/12472/13833、commit 92f87f2（MariaDB）；dev.mysql.com MEB 8.0 文档与发布说明（`--incremental=page-track` 8.0.18 默认、8.0.27 DDL 并行）；percona.com blog（PS 5.6 引入）、launchpad 5.5.27-29.0 milestone。

> **来源分级说明**：本节版本起点（MDEV 编号、commit、MEB/PS 发布）均为**联网佐证**，须在 MySQL/MariaDB/Percona 发行说明上独立复核；本项目仓内仅证得 PXB 端对 Percona 位图与官方 track 的消费判断。

**MariaDB 真增量核实（MDEV 证据，联网佐证）**：
- **MariaDB 10.1（XtraDB）确曾有插件式真增量**：`INFORMATION_SCHEMA.CHANGED_PAGE_BITMAPS` 插件（MYSQL_INFORMATION_SCHEMA_PLUGIN，MDEV-7472/commit b7ff5f1）承载 `FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS`；另有 `INNODB_CHANGED_PAGES` 表（SPACE_ID/PAGE_ID/START_LSN/END_LSN，log-thread 解析 redo 更新）+ `innodb_track_changed_pages`，供 mariabackup 10.1 只读位图页、免全扫描做真增量。
- 该插件仅存于 XtraDB（MariaDB 10.1）；**10.2+ 换 InnoDB 后废弃**：`innodb_track_changed_pages` 于 10.2.6 起 ignored，mariabackup 10.2+ 移除 bitmap（MDEV-18985），2024-02 commit 92f87f2 删除 changed_pages_bitmap 代码；MDEV-17102（于 InnoDB 重实现）未完成。
- mariadb-backup（10.2+）实际增量 = LSN 全表扫描比对（官方文档 "checks the most recent LSN … against the LSN's contained in the database"）；`--incremental-force-scan` 在 10.2+ 无意义（无 bitmap 数据）。
- 结论：**现行 MariaDB（10.2~11）无免全扫描物理真增量**；真增量仅三条：Percona Server（bitmap）、MySQL 8.0.27+（官方 page-tracking）、MariaDB 10.1/XtraDB（CHANGED_PAGE_BITMAPS 插件，已 EOL）。

---

### 三、第三方 / 业界其它增量技术 与 本项目缺失项

> 口径：`XtraBackup 8.0.25 是否已提供`。

| # | 方案 | 8.0.25 | 差异/原理 | 备注(URL) |
|---|------|:---:|------|------|
| 1 | **官方 page tracking 页级增量**（`--page-tracking`） | ❌缺失 | MySQL 8.0.17+ 的 IO 层按 LSN 记录落盘页，服务端返回页 list；只拷变化页，免全扫。8.0.27 起支持；需 mysqlbackup 组件、单文件系统表空间；有 DDL bug(#106163) | docs.percona.com/percona-xtrabackup/8.0/page-tracking.html |
| 2 | **MySQL Enterprise Backup (MEB) 增量** | ❌(需 MEB) | `mysqlbackup --incremental=page-track|full-scan|optimistic`；page-track 用官方页跟踪+redo 前滚，optimistic 受堵自动退化 full-scan；商业 | dev.mysql.com/doc/mysql-enterprise-backup/8.4/en/mysqlbackup.incremental.html |
| 3 | **MEB optimistic / full-scan 变异** | ❌(需 MEB) | 与 XtraFullScan 思路相似，但三态+自动退化更健壮 | backup-incremental-options.html |

---

### 四、结论与建议

1. **本项目（8.0.25）物理增量能力 = 「全表扫描比对页 LSN」+ （Percona Server）changed-page bitmap + history 续作**；其余为还原阶段（prepare）与备份一致性（Redo Log Archive）通用机制。
2. **最值得补齐的缺失特性 = 官方 page tracking（`--page-tracking`）**：自 8.0.27 起的核心能力，能显著降低增量 IO；本项目(8.0.25)尚需升级到 ≥8.0.27 才能获得。
3. 其他差距（MEB 三态算法）为「版本/商业」差异，不影响 8.0.25 作为基础增量工具使用；`--rollback-only/--redo-lag` 在本版本已移除。

## 参考资料

- 本项目源码：`storage/innobase/xtrabackup/src/`（write_filt / read_filt / changed_page_bitmap / redo_log / backup_mysql / xtrabackup）
- Percona 官方文档：page-tracking（https://docs.percona.com/percona-xtrabackup/8.0/page-tracking.html）；create-incremental-backup（.../8.0/create-incremental-backup.html）
- Percona 发布说明 8.4.0-3 / 8.4.0-6（docs.percona.com/percona-xtrabackup/8.4/release-notes/...）
- MySQL 官方：MEB incremental（dev.mysql.com/doc/mysql-enterprise-backup/8.4/en/mysqlbackup.incremental.html）；InnoDB Clone & page tracking 博客（dev.mysql.com/blog-archive/innodb-clone-and-page-tracking/）

---

## 附录 A. 代码证据清单（源码主证，路径 `storage/innobase/xtrabackup/src/`）

> 每条均标注 `file:line` 与原始代码片段。行号为 PXB 8.0.25-17 快照实际行号。

### A1. LSN 全表扫描增量（默认主路径）

**1. 写过滤安装（增量 → `wf_incremental`）** — `xtrabackup.cc:2906-2911`
```c
  /* Setup the page write filter */
  if (xtrabackup_incremental) {
    write_filter = &wf_incremental;
  } else {
    write_filter = &wf_write_through;
  }
```

**2. 逐页 LSN 判定（只拷变化页）** — `write_filt.cc:122-126`
```c
    if (cursor->space_id == dict_sys_t::s_space_id &&
        metadata_from_lsn > mach_read_from_8(page + FIL_PAGE_LSN))
      continue;
    else if (incremental_lsn > mach_read_from_8(page + FIL_PAGE_LSN))
      continue;
```

**3. delta 块魔数与结束标记** — `write_filt.cc:161-166`
```c
  if (cp->npages != page_size / 4) {
    mach_write_to_4(cp->delta_buf + cp->npages * 4, 0xFFFFFFFFUL);
  }
  /* Mark the final block */
  mach_write_to_4(cp->delta_buf, 0x58545241UL); /*"XTRA"*/
```
（起始魔数 `0x78747261 "xtra"` 见 `write_filt.cc:94,138`；页号表+页字节流见 `142-143`）

**4. 强制全扫描开关** — `xtrabackup.cc:884-888`（`--incremental-force-scan`）

**5. 位图缺失自动回退全扫描** — `xtrabackup.cc:4012-4021`
```c
  if (xtrabackup_incremental) {
    if (!xtrabackup_incremental_force_scan && have_changed_page_bitmaps) {
      changed_page_bitmap =
          xb_page_bitmap_init(redo_mgr.get_start_checkpoint_lsn());
    }
    if (!changed_page_bitmap) {
      msg("xtrabackup: using the full scan for incremental backup\n");
    }
```

### A2. Changed-Page-Bitmap（Percona Server 真增量）

**1. 服务端变量注册** — `backup_mysql.cc:511`（`{"innodb_track_changed_pages", &innodb_track_changed_pages_var}`）

**2. 仅 Percona Server 判真** — `backup_mysql.cc:683-686`
```c
  if (innodb_track_changed_pages_var != nullptr &&
      strcasecmp(innodb_track_changed_pages_var, "ON") == 0) {
    have_changed_page_bitmaps = true;
  }
```

**3. FLUSH 位图落盘** — `backup_mysql.cc:2179-2186`
```c
bool flush_changed_page_bitmaps() {
  if (xtrabackup_incremental && have_changed_page_bitmaps &&
      !xtrabackup_incremental_force_scan) {
    xb_mysql_query(mysql_connection,
                   "FLUSH NO_WRITE_TO_BINLOG CHANGED_PAGE_BITMAPS", false);
  }
  return (true);
}
```

**4. 构建位图区间（起点取全局 `incremental_lsn`）** — `changed_page_bitmap.cc:588-601`
```c
  if (!log_online_setup_bitmap_file_range(&bitmap_files, bmp_start_lsn,
                                          bmp_end_lsn)) {
    return NULL;
  }
  /* Only accept no bitmap files returned if start LSN == end LSN */
  if (bitmap_files.count == 0 && bmp_end_lsn != bmp_start_lsn) {
    return NULL;
  }
```

**5. 位图定位变化页（免全扫描核心）** — `read_filt.cc:137-154`
```c
    /* Find the next changed page using the bitmap */
    next_page_id = xb_page_bitmap_range_get_next_bit(ctxt->bitmap_range, TRUE);
    if (next_page_id == ULINT_UNDEFINED) { *read_batch_len = 0; return; }
    ctxt->offset = next_page_id * ctxt->page_size;
    ctxt->filter_batch_end =
        xb_page_bitmap_range_get_next_bit(ctxt->bitmap_range, FALSE);
```

### A3. 历史元数据续作

**1. 参数定义** — `xtrabackup.cc:403-404`（`opt_incremental_history_name/uuid`）

**2. 查询上次备份 `innodb_to_lsn`（name/uuid 两分支）** — `backup_mysql.cc:803-822`
```c
             "SELECT innodb_to_lsn "
             "FROM PERCONA_SCHEMA.xtrabackup_history "
             "WHERE name = '%s' "
             "AND innodb_to_lsn IS NOT NULL "
             "ORDER BY innodb_to_lsn DESC LIMIT 1",
```
（uuid 分支见 `811-822`；建表 `1872-1926`、写入 `1885-1892`）

### 缺口断言（全仓检索，主证）

| 缺失项 | 检索结果 |
|---|---|
| `--rollback-only` / `rollback_only` | 全仓无符号（exit=1） |
| `--redo-lag` / `redo_lag` | xtrabackup 目录无符号（NDB 的 `c_max_redo_lag` 无关） |
| `--page-tracking` CLI | xtrabackup 目录无该选项；仅文档提及 Percona changed page tracking（`doc/`）；引擎 `ha_innodb.cc:3950-4070` 存在 page_track API 但 xtrabackup 端无消费 |

> **佐证分级**：本附录 A1-A5 及缺口检索均为**源码主证**；MariaDB 10.1 XtraDB 插件、MEB/page-tracking 版本能力为**联网佐证**（见正文二.5 分级说明）。