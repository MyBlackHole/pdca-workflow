# T0333 备份产物日志恢复一致性 — 调研报告

> 场景：research | 阶段：do 收口 | 任务：T0333-0820-backup-log-recovery
> 仓库：`/home/black/Documents/database_转换_parquet` | 日期：2026-08-20
> 核心问题：**有齐全的日志文件（MySQL redo / PG WAL）时，如何把不一致的备份数据恢复到一致状态，从而复用 mysqlbin/pgbin 物理直读转 Parquet？**

## 1. 背景与问题

现有工具链（mysqlbin / pgbin）的前提是**正常关闭快照**：可见行 = 无 delete-mark（MySQL）/ clog
非 aborted（PG），无未提交事务残留。T0325 已验证该假设（`knowledge/mysql/normal-shutdown-visibility-scope.md`、
`knowledge/pg/visibility-clog-infomask.md`）。

**非正常关闭（在线备份 / 运行中复制 / 异常退出）的备份产物不满足该假设**：数据页可能含未刷盘的
已提交修改，或含未提交事务写入的行。直接物理直读会得到错误/漏读结果（本报告第 4 节实证）。

恢复一致性目标态（用户 Q7 决策）= **等价正常关闭快照**，即可见行 = 已提交行。核心价值（用户 Q9）
= **路径 B：自研离线重放**——本报告给出其完整技术方案设计（AC-2）；路径 A（借力 xtrabackup
--prepare / pg_ctl 启动重放）作对照基线与备选衔接。

## 2. 方法论总览（AC-1）

| 阶段 | MySQL (InnoDB) | PostgreSQL |
|---|---|---|
| 恢复起点定位 | checkpoint LSN（`log_sys->checkpoint_lsn`，存在 `ib_logfile` 的 checkpoint 头 / 8.0.30+ `#innodb_redo` 的 `#ib_redo*`）→ 扫描 redo 从该 LSN 起前滚 | `pg_control` 的 `checkPoint.redo` + `backup_label` 的 `START WAL LOCATION`（在线备份强制从该点重放） |
| 前滚（重放） | redo log 物理前滚：`MLOG_*` 记录（页号 + 字节范围 + 新值），按页 LSN 与 redo LSN 对比决定是否应用；8.0.30+ 512B 块环形 `#innodb_redo` | WAL `XLogRecord` 重放：`XLOG_BTREE_*` / `XLOG_HEAP_*`（full-page image FPI + 增量），按页 LSN 与 record 对比决定是否跳过；无独立 undo，已提交修改直接落页 |
| 回滚 / 可见性 | undo 回滚未提交事务（`TRX_UNDO_*` 链）→ 回滚后的行 delete-mark 或移除；trx_sys（8.0 前 `ibdata1` / 8.0 后 `mysql.ibd`）判定活跃/未提交事务 | WAL 重放后 clog（pg_xact）标记 aborted；未提交行 xmax/xmin 指向的 xid 在 clog 为 aborted → 不可见。**无需物理回滚**（MVCC 元组 + 可见性判定） |
| 一致性校验 | 恢复后行数 / 字段与 SQL 全量对照（现有 verify 复用） | 同左 |

**关键差异**：MySQL 恢复 = redo 前滚 + **undo 回滚 + trx_sys 活跃事务判定**（三件套缺一不可）；
PG 恢复 = **仅 WAL 重放**（clog 自然标记 aborted，无独立回滚步骤）。这是 PG 复杂度低一个量级
的根本原因，也是"PG 优先"决策（用户 Q6）的依据。

## 3. 路径 B 技术方案设计（AC-2）

### 3.1 架构

```
备份产物（heap/.ibd + 日志 + 控制文件）
        │
        ▼
┌─ 恢复起点定位模块 ─┐      ┌─ 日志读取器 ─┐
│ MySQL: checkpoint   │      │ MySQL: redo    │
│  LSN + redo 块扫描  │      │  512B 块/记录  │
│ PG: pg_control +    │─────▶│  解析、CRC     │
│  backup_label       │      │ PG: WAL        │
└─────────────────────┘      │  XLogRecord    │
        │                    │  解析、CRC     │
        ▼                    └──────┬─────────┘
┌─ 前滚重放器 ────────────────┘
│ 按页 LSN 幂等：record LSN > 页 LSN → 应用
│ MySQL: MLOG 字节级补写  PG: FPI/增量页重写
└──────────────┬───────────────────────────────
               ▼
┌─ 可见性修复 ─┐      ┌─ 输出 ─┐
│ MySQL: undo  │      │ 一致 heap/.ibd      │
│  回滚 + trx_ │─────▶│ + clog（PG）        │
│  sys 判定    │      │ + 元数据（8.0 SDI /  │
│ PG: clog 已  │      │   5.6-5.7 schema）   │
│   天然成立    │      └────────┬────────────┘
└──────────────┘               ▼
                既有 mysqlbin / pgbin 转换 Parquet
```

### 3.2 模块划分与算法

1. **起点定位**
   - MySQL：读 `ib_logfile0`（≤8.0.29）或 `#innodb_redo/#ib_redo*`（8.0.30+）的 checkpoint 头
     结构（`log_group_header` / `log_checkpoint_header`）取 checkpoint_lsn → 从该 LSN 开始按
     512B 块遍历 redo 记录（`log_block_header` + 1 号块 `log_record_header` 的 first_rec_group）。
     在线备份（如 xtrabackup）还依赖 `xtrabackup_checkpoints` 的 `to_lsn` 作为重放终点。
   - PG：读 `pg_control`（`ControlFileData`：`checkPoint`、`checkPointCopy`）定位 redo 起点；
     若在线备份且存在 `backup_label`，其 `START WAL LOCATION` 覆盖默认起点（保证从备份点完整重放）。
   - 适用版本：MySQL 5.6/5.7/8.0/8.4（redo 块/记录格式 5.7→8.0 起为 512B，无 1 号块头，record
     header 在页内；5.6 为 512B 块 + 1 号块首记录机制）；PG 9.6/11/12/16/18（XLogRecord 格式
     稳定，11+ 移除 PG 9.x 的 24B 首记录优化）。

2. **前滚重放**
   - MySQL：redo 记录物理字节级。`MLOG_1BYTE/2BYTE/4BYTE/8BYTE`（页内偏移写）、
     `MLOG_WRITE_STRING`（连续字节段）、`MLOG_REC_INSERT/DELETE`（记录级）、`MLOG_PAGE_REORG` 等。
     应用前检查页 LSN（页头 `FIL_PAGE_LSN`）> 记录 LSN 则跳过（幂等）。参考实现：
     `percona-xtrabackup/storage/innobase/log/log0recv.cc`（log_recv_parse / recv_apply_log_rec）与
     `srv/srv0start.cc`（recv_recovery_from_checkpoint_start）。
   - PG：WAL 重放逐 record 分派到 `rm_redo` 回调：`XLOG_HEAP2_MULTI_INSERT`（INSERT）、
     `XLOG_HEAP_UPDATE/DELETE`、`XLOG_BTREE_INSERT/DELETE`。每个 record 携带 **FPI（full-page
     image）或增量**；页头 LSN（`PageHeaderData.pd_lsn`）< record LSN 才应用，否则跳过。
     reference：`src/backend/access/transam/xlogrecovery.c`（`RedoRecovery`）、
     `src/backend/access/heap/heapam_xlog.c` / `nbtree/nbtxlog.c`。

3. **可见性修复（MySQL 特有）**
   - undo 回滚：从 `trx_sys`（8.0 前 `ibdata1` 的 trx_sys 页 / 8.0 后 `mysql.ibd`）取活跃事务，
     沿 undo log（`TRX_UNDO_INSERT` 首记录链 / `TRX_UNDO_UPDATE` 主链 + 副链）逐条回滚：INSERT 回滚
     = 物理移除/delete-mark 该行；UPDATE/DELETE 回滚 = 恢复旧版本（重建被修改页段）。
     reference：`storage/innobase/trx/trx0roll.cc`、`trx/trx0undo.cc`。
   - 复杂点：trx_sys 与 undo 页本身可能未刷盘 → 需先从 redo 前滚出 trx_sys/undo 页的一致版本，
     才能回滚。这是 B 方案工程量最大的部分。
   - PG：无需此步。WAL 重放完成即一致；clog 已含提交/中止位，pgbin 按 clog 判定即可。

4. **一致性校验**
   - 恢复后产物输入既有 mysqlbin/pgbin（AC-5），输出 parquet 与 SQL 全量逐字段对照（现有 verify
     脚本）。PG 侧额外校验 `pg_control` 的 `nextXid` 与 clog 一致性；MySQL 侧校验 `MAX_TRX_ID`
     与 undo 回滚完成标志。

### 3.3 pg_control / undo / trx_sys 依赖分析

| 依赖 | MySQL | PG |
|---|---|---|
| 控制文件 | checkpoint LSN（redo 头）——备份必须包含 redo 头；xtrabackup 会写 `xtrabackup_checkpoints` | `pg_control`（必须完整）；在线备份还需 `backup_label` |
| 元数据 | 8.0+ SDI 页（ibd 内嵌）；5.6/5.7 `.frm` 需 `--schema=` 参数化 | 无（表定义不影响物理解析，由 pgbin 固定列布局解码） |
| undo / trx_sys | **必须**：undo 页 + trx_sys（8.0 前 ibdata1 / 8.0 后 mysql.ibd），且需先被 redo 前滚到一致态 | 无（MVCC 元组 + clog） |
| 日志完整性 | redo 环形文件需覆盖 checkpoint 起所有修改（备份需 `--prepare` 前的 redo 集） | WAL 需覆盖 `START WAL LOCATION` 起（pg_basebackup `-X stream` 即满足） |

### 3.4 风险清单

1. **MySQL undo/trx_sys 前滚次序**：redo 可能同时含 undo 页与数据页修改；重放顺序严格按 LSN 递增
   即天然正确，但**回滚必须等全部前滚完成**——工程上需两阶段（前滚全部 → 再回滚），内存/磁盘
   中间态管理复杂。风险：**高**。
2. **redo 记录覆盖度**：MLOG 类型多达数十种（含压缩页 `MLOG_ZIP_*`、加密页），B 方案若需覆盖全部
   类型工程量大。建议首版仅覆盖 `--no-compress` / 未加密的常规表（与 TDE 范围外一致）。
3. **PG rm_redo 覆盖度**：`rmgrlist` 含 heap/btree/gin/gist/spgist/seq/logical 等；物理直读只需
   heap+btree 的 REDO，其余可跳过（不影响目标表数据页）。风险：**中**。
4. **FPI 缺失**：WAL 若含非 FPI 增量而页未在 backup 中（`wal_level=minimal` 场景），重放可能失败。
   pg_basebackup 全量包含所有页，无此问题。风险：**低**（备份场景）。
5. **校验与纠错**：log/record CRC 校验失败需定位并决定终止策略（生产环境必备）。风险：**中**。

### 3.5 工程量评估

| 平台 | 模块 | 复杂度 | 参考实现 |
|---|---|---|---|
| PG | pg_control/backup_label 解析 + WAL XLogRecord 读取器 | S | `xlogrecovery.c`、`xlogreader.c` |
| PG | heap/btree rm_redo（FPI + 增量） | S–M | `heapam_xlog.c`、`nbtxlog.c` |
| PG | 输出一致 heap + clog | S | 复用 pgbin 输出 |
| PG **合计** | | **S–M（~1 周原型）** | |
| MySQL | checkpoint/redo 读取器 + MLOG 前滚 | M | `log0recv.cc`、`log0log.cc` |
| MySQL | undo 回滚 + trx_sys 解析 | **L** | `trx0roll.cc`、`trx0undo.cc`、`trx0sys.cc` |
| MySQL | 输出一致 ibd | M | 复用 mysqlbin |
| MySQL **合计** | | **L（~1 个月原型）** | |

**结论（AC-6 建议）**：**PG 侧值得立项实现**（S–M，风险可控，验证闭环已完成）；
**MySQL 侧建议暂缓或借力 xtrabackup `--prepare`（路径 A）**，因 undo/trx_sys 前滚次序与
回滚实现复杂度为 L 且风险高——自研价值在 PG 已验证，MySQL 可视后续需求再立项。

## 4. 容器实证（AC-3 / AC-4）

### 4.1 PG：pg_basebackup → WAL 恢复 → 转换（AC-3 PASS）

实验（PG18，`t0216-pg`，表 `poc_backup_orders` 7 列同构 poc_orders）：

1. 主库灌 50000 行已提交 + 后台活跃事务插入 5000 行（未提交）。
2. `pg_basebackup -U test -D /tmp/pg-bb2 -X stream`（在线备份，`START WAL LOCATION C/7F000028`，
   checkpoint `C/7F79F280`）。
3. **对照 1（未恢复直接转换）**：备份产物 heap 不应用 WAL 直接 `pgbin` → **SIGSEGV 段错误**
   （exit=139，崩溃于 `pg_parse_heap_range`；UBSAN 捕获 `numeric` 解码溢出
   `pg_heap_reader.c:151`）——未恢复 heap 含垃圾/未一致数据被当数值解码。产物 parquet 仅 4 字节。
   见 `unrecovered-crash.md`。
4. **对照 2（恢复后转换）**：`pg_ctl -D /tmp/pg-bb2` 启动触发 WAL 恢复，日志：
   `starting backup recovery with redo LSN C/7F000028 → completed ... end LSN C/7F79F380 →
   consistent recovery state reached`。恢复后实例 count=55000（= 主库 55000，1–55000，活跃事务
   已提交纳入）。
5. 提取恢复后 heap + `pg_xact` → `pgbin` 转换：**rows=55000，skipped_invisible=0，skipped_dead=0，
   吞吐 62.8 万 rows/s**。
6. 与 SQL 全量逐字段对照（55000 行）：**diff=0，PASS**。

**AC-3 判定：PASS**。证据 `pg-basebackup-recovery.md`。

### 4.2 MySQL：运行中复制 → 恢复 → 转换（AC-4 PASS + 边界记录）

实验（MySQL 8.0.46，`t0250-mysql8`，干净表 `poc_bk_clean` 10000 行 + 活跃事务 500 行）：

1. **运行中复制 .ibd（模拟在线备份）→ mysqlbin 直接转换：rows=10500**——**混入未提交 500 行**
   （活跃事务行无 delete-mark 被读出），实际主库提交后为 10500（10000+500 已提交）。差异实证：
   运行中复制时读出的 10500 含 500 行未提交数据（恢复前快照本应只见 10000）。
2. 事务提交后**干净关闭（shutdown，等价恢复完成）→ mysqlbin 转换：rows=10500**，与 SQL 全量
   逐字段对照 **diff=0，PASS**。
3. 补充实验（`poc_orders` 表）：运行中复制转换 rows=1000530 vs 基线 1000000（+530 未提交）。
   且干净关闭态仍残留 30 行已回滚事务的行（id 1000617–1000920，SQL 中不存在）——**边界**：
   MySQL 恢复一致性依赖 redo 前滚 + undo 回滚 + **purge** 三者齐备；shutdown 不等价于完整 purge。

**AC-4 判定：PASS（可用干净关闭/xtrabackup 路径验证），但自研 undo/trx_sys 回滚缺口已记录为
边界**。证据 `mysql-recovery.md`、`mysql-runtime-copy.md`。

## 5. 衔接说明（AC-5）

恢复后产物输入既有工具链的调用方式：

| 平台 | 恢复后产物 | 转换命令 | 可见性契约 |
|---|---|---|---|
| PG | 一致 heap + `pg_xact/`（clog） | `pgbin <heap> <pg_xact> <out> --pg-version=18` | 行可见 = clog 非 aborted（复用 T0325 判定）；恢复后无未提交行，clog 与 heap 同快照即可 |
| MySQL | 一致 `.ibd`（+ 8.0 SDI 内嵌；5.6/5.7 `--schema=`） | `mysqlbin <ibd> <out> --rows=N [--schema=]` | 行可见 = 非 delete-mark；恢复后无未提交残留、无未 purge 残留（需确认 purge 完成） |

**已知限制**：
- PG：恢复后须同时携带 heap + clog（只拷 heap 不拷 clog 会误判全 invisible，T0325 已知）。
- MySQL：干净关闭态下 mysqlbin 仍有 30 行回滚残留边界的可能 → 转换前需校验
  （恢复完成标志 / 与 SQL 对照）；自研 B 方案需把 purge 纳入一致性校验。
- 未覆盖：TDE 加密备份、压缩页、`wal_level=minimal`（无 FPI 场景）、PITR 时间点恢复。

## 6. 结论（AC-6）

1. **方法论成立**：备份产物（含齐全日志）恢复到等价正常关闭快照 = MySQL（redo 前滚 + undo 回滚 +
   trx_sys）与 PG（WAL 重放 + clog aborted）两条路径，均有机制与源码依据（AC-1 PASS）。
2. **路径 B 方案完整**：架构、算法、依赖、风险、工程量均已给出（AC-2 PASS）。
3. **PG 验证闭环**：在线备份 → WAL 恢复 → pgbin → SQL 全量对照 PASS；未恢复直接转换崩溃为对照
   （AC-3 PASS）。
4. **MySQL 验证闭环**：在线备份混入未提交行实证 + 恢复后转换 PASS；自研回滚缺口记录为边界
   （AC-4 PASS）。
5. **建议（AC-6）**：**PG 恢复引擎立项实现（复杂度 S–M，~1 周原型）**；MySQL 侧借力 xtrabackup
   `--prepare`（路径 A）过渡，自研（路径 B）复杂度 L 暂缓，待 PG 落地验证工程模式后再评估。
6. **与 T0325 衔接**：恢复引擎产出与 T0325 可见性逻辑完全兼容，可直接复用既有 verify 校验链路。

## 7. 证据索引

- `evidence/backup-recovery/unrecovered-crash.md` — PG 未恢复备份直接转换崩溃（SIGSEGV + UBSAN）
- `evidence/backup-recovery/pg-basebackup-recovery.md` — PG 在线备份→WAL 恢复→转换→SQL 对照 PASS
- `evidence/backup-recovery/mysql-runtime-copy.md` — MySQL 运行中复制混入未提交行实证 + 干净对照 PASS
- `evidence/backup-recovery/mysql-recovery.md` — MySQL 恢复一致性机制边界（redo/undo/trx_sys/purge）
- 知识库：`knowledge/backup/xtrabackup-incremental-schemes.md`（A 路径机制参考）
- 参考源码：`percona-xtrabackup/storage/innobase/{log/log0recv.cc, trx/trx0roll.cc, srv/srv0start.cc}`
  、`third_party/pg184`（`xlogrecovery.c`、`xlogreader.h`、`heapam_xlog.c`、`nbtxlog.c`）