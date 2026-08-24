# 附录：T0389 后续追问深度分析（Q&A 与代码证据汇总）

基准源码：percona-xtrabackup-8.0.25-17 | 归档任务：pdca/tasks/archive/2026-08/0824-checksum-mismatch-datafile
生产案例：`./usercdb/ur_usergoods_info_his_06#p#p2026.ibd, Space ID:520513, Flags:16417`
本文档为 conclusion.md / research-report.md 的问答式延伸记录，所有 file:line 均已在源码树验证。

---

## QA1. 报错是否影响本次备份？

**结论：是——静默缺文件。**

因果链四跳（每跳可验证）：

```
① validate_first_page() 失败 → 打印报错          (fsp0file.cc:638+657)
② fil_open_for_xtrabackup 提前 return            (fil0fil.cc:11733-11735)
③ fil_space_create/fil_node_create 未执行 → space 未进 fil_system 内存缓存
④ backup 拷贝枚举 datafiles_iter_new → Fil_iterator::for_each_file
   → fil_system->iterate() 只遍历已注册 space     (xtrabackup.cc:496-509)
   → 该 .ibd 不被复制
⑤ open_ibds() 忽略返回值 → 备份继续、正常结束     (fil0fil.cc:2344-2351)
```

后果：备份显示成功，但该分区不在备份集；恢复后访问此分区报表空间缺失；
redo 无法补救（逐页复制根本未发生）；元数据 xtrabackup_tablespaces 来自
I_S.FILES（space_map.h:61, xtrabackup.cc:3995,4152），来源独立于拷贝列表，
**元数据有 ≠ 物理文件在**。

确认命令：
```bash
find <backup_dir>/usercdb -name 'ur_usergoods_info_his_06#p#p2026.ibd'
grep '520513' <backup_dir>/xtrabackup_tablespaces
```

## QA2. 是否影响后续备份？

| 场景 | 表现 |
|------|------|
| 进程能力 | 零影响：单文件失败被忽略，各 space 独立注册，下次备份重新扫描 |
| 根因为瞬态（窗口冲突/torn 被扫到） | 下次自愈 |
| 根因为稳定损坏（存储坏块） | 每个备份周期持续静默丢同一分区，丢失窗口扩大 |
| **增量备份链** | **断裂风险**：--incremental 同走 datafiles_iter_new（xtrabackup.cc:4034）。全量缺文件 → 后续增量校验通过产生 .delta → --prepare --incremental-dir 时 base 无对应 .ibd → 整条增量链不可恢复 |
| 假自愈陷阱 | DROP PARTITION 后报错消失 ≠ 修复，历史受损备份仍不可恢复 |

## QA3. 报错只在读取首页异常时出现吗？

**是。** `Datafile::validate_first_page()` 仅读 page 0 校验（fsp0file.cc:561-563
read_first_page；:552-665 全程基于第一页缓冲）。

三种首页状态对应三种文案：

| 首页状态 | 文案 | 位置 |
|----------|------|------|
| IO 读失败 | Cannot read first page | fsp0file.cc:563 |
| 整页全零 | Header page consists of zero bytes（backup 场景豁免放行 fil0fil.cc:11729） | fsp0file.cc:584 |
| 读到但校验失败 | **Checksum mismatch in datafile** | fsp0file.cc:638+657 |

校验失败分支不止 checksum 字段：加密页类型未解密（checksum.cc:274-280）、
LSN 头尾不一致 torn（:296-305）、双字段全算法回退链不匹配（:364-491）任一命中
都归并为此文案。非首页损坏走逐页复制路径，文案为
"Database page corruption detected at page N"（fil_cur.cc:407）。

## QA4. 备份操作流程图与问题位置

### 4.1 主流程（★=问题位置）

```
xtrabackup --backup 启动
       │
       ▼
① 初始化：打开系统表空间 ibdata
   (xb_load_tablespaces, xtrabackup.cc:3252)
   注：ibdata 首页校验 read_lsn_and_check_flags 被
   #ifndef UNIV_HOTBACKUP 排除(fsp0sysspace.cc:525)，backup 中不编译
       │
       ▼
② 扫描 datadir 全部 .ibd → 逐个打开注册
   (open_ibds → fil_open_for_xtrabackup, fil0fil.cc:2344→11718)
      ★1 首页校验失败 → 打印报错        (fsp0file.cc:638)
      ★2 提前返回 → 分区未注册          (fil0fil.cc:11733-11735)
      ★4 返回值被忽略 → 处理下一个      (fil0fil.cc:2344-2351)
       │
       ▼
③ 元数据收集(来源 I_S.FILES，与拷贝列表相互独立, xtrabackup.cc:3995)
       │
       ▼
④ 启动 redo 拷贝线程("log scanned up to ..." 周期输出)
       │
       ▼
⑤ N 线程并行逐页拷贝(datafiles_iter_new :496)
      ★3 只遍历已注册清单 → ★2 缺席文件在此被跳过
      页级失败重试10次→另一条文案(fil_cur.cc:386-414)
       │
       ▼
⑥ 写 xtrabackup_tablespaces(:4152) → completed OK!(无 error)
```

图例：─▶ 流转方向；★n 问题位置编号

### 4.2 首页判定决策流

```
读 page0 ─┬─ IO失败 ──→ "Cannot read first page"
          ├─ 全零 ────→ 豁免放行(DB_PAGE_IS_BLANK, redo 后补)
          ├─ flags/page_no/space_id 异常 ──→ 各自独立文案
          └─ is_corrupted(): 加密未解密 / torn / 双checksum不匹配
                任一命中 ═══▶ ★ "Checksum mismatch in datafile"
             全部通过 ──→ 注册成功 → 进入⑤拷贝
```

图例：│├└ 决策分支；═▶ 归并为同一报错文案

## QA5. 为什么可能是"分区维护窗口冲突"(R9)

三要素交汇：

1. **分区 DDL 制造中间态文件**：REORGANIZE/REBUILD/OPTIMIZE = 删旧 .ibd 建
   新 .ibd 逐步搬数据；新文件首页（FSP 头/flags/space_id 回填）多次覆写，
   每次 pwrite 16KB 跨扇区非原子，读者可见半新半旧状态。
2. **xtrabackup 无锁旁路读**：直接 pread 物理文件视图，不感知 InnoDB 写入进度。
3. **结构性不对称（核心）**：同一中间态页，拷贝阶段给 10 次×100ms 重试等它写完
   （fil_cur.cc:313, 注释原文 *"in case of partially written pages"* :352-353），
   扫描阶段一次失败即放弃该文件。

佐证信号：p2026 为活跃年份分区必然持续写入；19:00 备份窗口与常见夜间归档/
分区调度重叠；Space ID=520513 量级大侧面反映实例频繁做过分区 DDL。

证实/证伪：D3 重跑单库备份看瞬态性；比对报错时刻与 GoldenDB 分区调度日志；
innochecksum 全文件扫描排除稳定损坏。

## QA6. 原子 DDL 为什么没有覆盖这个场景（R9 表述精炼）

- 原子 DDL 保护的是**数据字典/binlog/引擎状态的崩溃恢复一致性**（面向 SQL 会话），
  不保证物理文件对旁路进程的原子可见性——REORGANIZE 的新 .ibd 自 create 起
  即对目录遍历裸露，与字典事务是否提交无关。
- 但并发窗口比初版报告表述的窄，两个已验证事实：
  - `--lock-ddl` 默认 on（xtrabackup.cc:955 def_value=1；:6892 opt_no_lock/
    opt_no_backup_locks 可关闭）；
  - 时序为先锁后扫：main → xb_init():7595 → lock_tables_for_backup():6979
    （LOCK INSTANCE FOR BACKUP, backup_mysql.cc:1089）成功后才进入
    xtrabackup_backup_func() → 扫描 :3998。该锁等待活跃 DDL 结束并阻塞新 DDL。
- 因此 R9 精确化为"**扫描瞬间命中非自洽首页**"，成立条件收窄：
  ① 生产显式关闭 lock-ddl（GoldenDB 多分库并行备份常见，需查脚本参数裁决）；
  ② 锁只挡 DDL 不挡 DML——普通刷脏 torn 态（R2）无需 DDL 即可撞上；
  ③ 底层弱点不变：扫描零重试 vs 拷贝 10 次重试的不对称。

## QA7. 零重试 vs mysqld 启动三层容错（代码证据）

### 7.1 xtrabackup 扫描路径（零容错）

```cpp
// fil0fil.cc:2344-2351  open_ibds：纯循环无 retry，返回值丢弃
void Tablespace_files::open_ibds() const {
  for (auto path : m_ibd_paths)
    for (auto name : path.second)
      fil_open_for_xtrabackup(m_dir.path() + name,
                              name.substr(0, name.length() - 4));
}

// fil0fil.cc:11727-11735  一次判定即返回
err = file.validate_first_page(SPACE_UNKNOWN, &flush_lsn, false);
if (err == DB_PAGE_IS_BLANK)      { return (DB_SUCCESS); }
else if (err != DB_SUCCESS)       { return (err); }   // ← 一枪毙命
```

对照——拷贝路径的重试设计（同属 xtrabackup 二进制）：

```cpp
// fil_cur.cc:313 / :352-353 / :399-413
retry_count = 10;
/* check pages for corruption and re-read if necessary.
   i.e. in case of partially written pages */
...
retry_count--;
if (retry_count == 0) { /* failed to read page after 10 retries */ }
std::this_thread::sleep_for(std::chrono::milliseconds(100));
goto read_retry;
```

### 7.2 mysqld 启动的三层兜底（均 #ifndef UNIV_HOTBACKUP 或运行期机制）

**层 A：ibdata 首页专项——重试×2 + doublewrite 恢复**

```cpp
// fsp0sysspace.cc:525
#ifndef UNIV_HOTBACKUP
dberr_t SysTablespace::read_lsn_and_check_flags(lsn_t *flushed_lsn) {
  ...
  // :552-561
  for (int retry = 0; retry < 2; ++retry) {
    err = it->validate_first_page(it->m_space_id, flushed_lsn, false);
    if (err != DB_SUCCESS &&
        (retry == 1 || it->restore_from_doublewrite(0) != DB_SUCCESS)) {
      it->close();
      return (err);              // 重试+dblwr 恢复都败才放弃
    }
  }

// fsp0file.cc:941  从崩溃恢复缓存找 page 0 完整副本
const byte *page = recv_sys->dblwr->find(page_id);
```

**层 B：崩溃恢复期对用户 .ibd 全部页的 doublewrite 修复**

```cpp
// buf0dblwr.cc:2193-2202  数据文件页损坏则从 dblwr 找副本
BlockReporter data_file_page(true, buffer.begin(), page_size, ...);
if (data_file_page.is_corrupted()) {
  ib::info(ER_IB_MSG_DBLWR_1315) << "Database page corruption or a failed "
      "file read of page " << page_id << ". Trying to recover it from the "
      "doublewrite file.";

// :2237-2258  完整副本覆写回数据文件
err = fil_io(write_request, true, page_id, page_size, 0, ...);
ib::info(ER_IB_MSG_DBLWR_1308) << "Recovered page " << page_id
                               << " from the doublewrite buffer.";
#endif /* !UNIV_HOTBACKUP */     // ← :2270 xtrabackup 不编译
```

**层 C：恢复期"全新页"豁免**

```cpp
// buf0buf.cc:5620-5627  崩溃扩文件的半零页不算损坏，交 redo 重放修复
if (recv_recovery_is_on() && (is_corrupted || is_wrong_page_id) &&
    recv_page_is_brand_new((buf_block_t *)bpage)) {
  memset(frame, 0, bpage->size.logical());
  is_corrupted = false;
}
```

### 7.3 对比总结

| 维度 | mysqld 启动/恢复 | xtrabackup 扫描 |
|------|------------------|------------------|
| 重试 | ibdata 首页 retry×2；恢复期 redo 反复重放 | 0 次 |
| doublewrite 兜底 | restore_from_doublewrite / dblwr_recover_page | 不可用（UNIV_HOTBACKUP 不编译，backup 进程无 recv_sys 框架） |
| 失败粒度 | 页级修复后继续 | 文件级放弃 |
| 失败后果 | 修不好才 fatal，数据原地不动 | 分区静默缺席备份集且备份照常 OK |

根因是编译与架构层面的：xtrabackup 以 UNIV_HOTBACKUP 编译，mysqld 的三套
兜底机制均不在其进程内生效；它面对中间态页只有"盲等写入完成"（拷贝路径）
和"直接放弃"（扫描路径）两种朴素手段。

---

## 排查动作优先级（贯穿各 QA 的落地清单）

1. D0：核对既有备份集是否缺该分区（find + grep 元数据），缺则补备；
2. 查生产备份命令行是否含 --no-lock/--lock-ddl=false（一票裁决 R9 窗口）；
3. D3 重跑单库备份判瞬态性；瞬态 → 分区调度避开备份窗口；
4. 稳定复现 → innochecksum 全文件扫描定位范围，评估 CHECK TABLE/重建分区；
5. 若使用增量策略：全量缺失期间产生的增量链整体视为不可信。
