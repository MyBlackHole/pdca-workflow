# 调研报告：XtraBackup "Checksum mismatch in datafile" 根因分析

任务：T0389 | 场景：research | 基准源码：percona-xtrabackup-8.0.25-17（GoldenDB 定制源码树）
生产案例：`./usercdb/ur_usergoods_info_his_06#p#p2026.ibd, Space ID:520513, Flags:16417`

## 调研目标

1. 报错的精确产生位置与判定逻辑；
2. `--backup` 阶段触发链路；
3. **报错是否影响备份**（用户核心关切）；
4. 全部可能根因与现场可执行的排查决策树。

## 方法

以本仓库源码为一手证据（primary source），逐条结论回溯到具体函数与行号；
生产日志作为案例输入解码交叉验证；全部结论给出可重跑的 grep/命令验证途径。
无法用代码证实的项（如存储层故障）明确降级为假设并标注置信度。

## 发现

### F1. 报错的精确拼接点（对应 AC-1）

- `"Checksum mismatch"` 写死于 `Datafile::validate_first_page()` 内
  （storage/innobase/fsp/fsp0file.cc:638），后缀文案在 :657 拼接：
  `"Checksum mismatch in datafile: <filepath>, Space ID:<id>, Flags:<flags>."`
  加 troubleshooting 链接，经 `ib::error(ER_IB_MSG_399)` 输出。
- 仅当表空间**第一页（page 0）**被 `BlockReporter::is_corrupted()` 判为损坏时触发
  （fsp0file.cc:633-639）。该函数只校验首页，不代表全文件状态。

验证途径：`grep -rn "Checksum mismatch" storage/innobase/` → 唯一命中 fsp0file.cc:638。

### F2. 判定内核全部分支（对应 AC-2）

`BlockReporter::is_corrupted()`（storage/innobase/buf/checksum.cc:285-495）按序判定：

| # | 分支 | 行号 | 说明 |
|---|------|------|------|
| B1 | 加密页类型即损坏 | checksum.cc:274-280, 292-294 | 页类型为 FIL_PAGE_ENCRYPTED / COMPRESSED_AND_ENCRYPTED / ENCRYPTED_RTREE 时直接判损坏（调用方未解密场景） |
| B2 | Torn page 检测 | checksum.cc:296-305 | 非压缩页：offset 22-25（FIL_PAGE_LSN+4）≠ 页尾 offset 16380-16383（page_size-FIL_PAGE_END_LSN_OLD_CHKSUM+4）→ 半页写入特征 |
| B3 | 算法短路放行 | checksum.cc:311-314 | algorithm=NONE 或 skip_checksum（系统临时表空间，fsp0fsp.cc:311-313 fsp_is_checksum_disabled）→ 直接通过 |
| B4 | 压缩页 zip 校验 | checksum.cc:316-318, 571-708 | ROW_FORMAT=COMPRESSED 表空间走 verify_zip_checksum（CRC32/adler 变体+兼容回退链） |
| B5 | 双字段校验和 | checksum.cc:320-491 | 页头 field1(offset 0) 与页尾 field2(offset 16376) 须通过当前算法及兼容回退链之一：CRC32 → CRC32 legacy big-endian → InnoDB 新旧公式 → BUF_NO_CHECKSUM_MAGIC；非 strict 模式下回退链全开，strict_* 只认单一算法 |
| B6 | 全零空页豁免 | checksum.cc:330-353 | field1=field2=LSN=0 且整页零 → 合法空页；**UNIV_HOTBACKUP 编译下跳过逐字节复核循环**（:335 条件编译） |

关键编译差异：XtraBackup 以 UNIV_HOTBACKUP 编译——
- buf_page_lsn_check 为空操作（checksum.cc:164），不做页 LSN vs redo checkpoint 比对；
- 默认 `srv_checksum_algorithm=SRV_CHECKSUM_ALGORITHM_INNODB`（checksum.cc:55），
  但实际由 sysvar 覆盖为默认 **CRC32**（ha_innodb.cc:21401）。

验证途径：阅读上述行号区间；`grep -n "UNIV_HOTBACKUP" storage/innobase/buf/checksum.cc`。

### F3. --backup 阶段触发链（对应 AC-3）

```
xtrabackup --backup
 └─ xb_load_tablespaces()                        [xtrabackup.cc:3252]
     ├─ srv_sys_space.check_file_spec(false,0)   [xtrabackup.cc:3265] 仅查规格，不校验页
     ├─ srv_sys_space.open_or_create(...)        [xtrabackup.cc:3273] 打开 ibdata
     │    注：read_lsn_and_check_flags 内的 validate_first_page 被
     │    #ifndef UNIV_HOTBACKUP 排除（fsp0sysspace.cc:525），ibdata 不走此校验
     └─ xb_scan_for_tablespaces()                [xtrabackup.cc:2259]
         └─ fil_scan_for_tablespaces(true) → Tablespace_files::open_ibds()
             └─ 对每个 .ibd: fil_open_for_xtrabackup(path,name) [fil0fil.cc:2344-2351, 11718]
                 ├─ Datafile::open_read_only(true) → validate_first_page [fsp0file.cc:478]
                 └─ validate_first_page(SPACE_UNKNOWN,&flush_lsn,false) [fil0fil.cc:11727]
                     ├─ err=DB_PAGE_IS_BLANK → 放行（fil0fil.cc:11729-11733，
                     │   "could be just zero-filled page, restored from redo log later"）
                     └─ err=DB_ERROR(含 Checksum mismatch) → return err [fil0fil.cc:11734-11735]
```

要点：**能报出此错误的必是非零但校验失败的首页**；全零首页已被豁免。
外部表空间同样经 `fil_open_for_xtrabackup`（xtrabackup.cc:3302-3305）。

### F4. 是否影响备份：是——静默缺文件（对应 AC-8，用户核心关切）

因果链（每一跳均已代码验证）：

1. `validate_first_page()` 失败 → `fil_open_for_xtrabackup` 在注册前提前返回
   （fil0fil.cc:11733-11735），`fil_space_create()/fil_node_create()` 不执行
   （fil0fil.cc:11760-11782）→ 该 space **未进入 fil_system 内存缓存**；
2. 备份拷贝线程的文件枚举器 `datafiles_iter_new()` 通过
   `Fil_iterator::for_each_file → Fil_iterator::iterate → fil_system->iterate()`
   收集待复制列表（xtrabackup.cc:496-509；fil0fil.h:1532-1550）——
   **只遍历已注册 space**；
3. 结论：该 .ibd **不会被复制进备份集**；
4. 但 `open_ibds()` 与外部文件循环均忽略返回值
   （fil0fil.cc:2344-2351；xtrabackup.cc:3302-3305）→ 备份继续、正常结束、无 error；
5. 元数据 `xtrabackup_tablespaces` 由 `Tablespace_map::scan(mysql_connection)`
   从 MySQL 层 I_S.FILES 生成（space_map.h:61；xtrabackup.cc:3995, 4152），
   来源独立于实际拷贝列表 → **元数据可能仍记录该分区，但物理文件缺失**。

后果分级：
- 该分区数据丢失于备份集；恢复+prepare 后访问该分区报表空间缺失；
- redo apply 无法补救（逐页复制根本未发生）；
- 若该分区随后被 DROP/REORGANIZE，损害可能被掩盖或延后暴露。

验证途径：
```bash
grep -n "return (err)" storage/innobase/fil/fil0fil.cc        # 11735 提前返回
sed -n '496,509p' storage/innobase/xtrabackup/src/xtrabackup.cc  # datafiles_iter_new
grep -rn "fil_system->iterate" storage/innobase/fil/fil0fil.cc   # 枚举来源
```

### F5. 生产案例逐字段解码（对应 AC-7）

Flags=16417=0x4021，按 fsp0types.h 位布局（:230-294 宽度/位置宏）：

| 字段 | 位 | 值 | 含义 |
|------|----|----|------|
| POST_ANTELOPE | 0 | 1 | post-Antelope 行格式标记 |
| ZIP_SSIZE | 1-4 | 0 | **非压缩表**（排除 R5） |
| ATOMIC_BLOBS | 5 | 1 | DYNAMIC 行格式特征 |
| PAGE_SSIZE | 6-9 | 0 | 16K 页大小 |
| DATA_DIR/SHARED/TEMPORARY | 10-12 | 0 | 本地/独享/持久 |
| ENCRYPTION | 13 | 0 | **未加密**（排除 R3） |
| SDI | 14 | 1 | 含 Serialized Dictionary Information |

Space ID 520513：GoldenDB 大规模分库分表环境典型的大 space id 区间。
文件名 `..._his_06#p#p2026.ibd`：历史表按年分区，2026 为活跃年份分区，
备份运行时（19:00:42）大概率正被业务写入或分区维护任务触碰；
报错与 `log scanned up to` 同秒出现，确认处于 backup 运行期。

本案根因优先级排序（置信度从高到低）：

| 排序 | 根因 | 置信度 | 一句话理由 |
|------|------|--------|-----------|
| 1 | R9 分区维护窗口冲突（DDL 重建中扫描到中间态首页） | 中 | 活跃年分区+备份时刻重叠；代码证明扫描期读到中间态即报错 |
| 2 | R2 torn page（首页半写状态被扫描到） | 中 | B2 分支正是此类特征；有 doublewrite 时概率低但扫描时机可撞上 |
| 3 | R1 首页真实损坏（存储坏块） | 中低 | 需 hexdump/innochecksum 复核才能证实/证伪 |
| 4 | R4 strict 算法配置 | 低 | 默认 CRC32 非 strict 兼容链全开，仅显式 strict_* 才可能 |
| — | R3 keyring / R5 压缩 | 已排除 | Flags 解码 ENCRYPTION=0、ZIP_SSIZE=0 |
| — | R8 GoldenDB 定制引入 | 待验证(低) | 源码树未见定制标记且无 git 历史可 diff |

验证途径（现场执行）见下方决策树 D 系列。

### F6. 根因清单全集（对应 AC-4）

| # | 根因 | 代码依据 | 现场观测特征 |
|---|------|---------|-------------|
| R1 | 首页真实损坏 | B5 校验失败 | hexdump 异常模式；innochecksum 多页报错且稳定复现 |
| R2 | Torn write | B2 LSN 尾比对 | 尾 4B ≠ 头 LSN 高 4B；瞬态（重跑消失）指向扫描时机 |
| R3 | 加密 key 缺陷 | B1+FSP ENCRYPTION 位 | ENCRYPTION=1 且 keyring 缺失/轮换；本案已排除 |
| R4 | strict 算法不匹配 | B5 回退链仅非 strict 生效 | my.cnf 显式 strict_*；改非 strict 后消失 |
| R5 | 压缩页失败 | B4 zip 校验 | ZIP_SSIZE≥10；本案已排除 |
| R6 | 截断/junk 尾页边界错位 | fil_cur.cc:296-309 对照 | 文件字节数 % 页大小 ≠ 0 |
| R7 | 版本混用 legacy 校验和 | B5 legacy big-endian/old innodb 分支 | 跨大版本升级实例；legacy 回退通常静默通过，strict 才暴露 |
| R8 | GoldenDB 定制偏差 | 无直接证据 | 无 git 历史 diff 可用，保持低置信度 |
| R9 | 分区维护窗口冲突 | F3 扫描时机 vs ADD/REORGANIZE/REBUILD PARTITION | 报错时间与分区调度重叠；重跑即恢复 |

### F7. 排查决策树（对应 AC-5；命令可直接复制执行）

设 `$BD=<datadir>/usercdb`，`$F=$BD/ur_usergoods_info_his_06#p#p2026.ibd`。

**D0. 先判定影响面（最优先）**
```bash
# 该分区是否真的进了最近一次备份集？
find <backup_dir>/usercdb -name 'ur_usergoods_info_his_06#p#p2026.ibd'
grep 'ur_usergoods_info_his_06#p#p2026' <backup_dir>/xtrabackup_tablespaces
# 物理文件缺失而元数据存在 → 该备份不可恢复此分区（F4 结论），需补备
```

**D1. 首页十六进制复核（判 R1/R2）**
```bash
xxd -l 40 -g 4 "$F"                      # 页头：off0 chksum1 / off4 page_no(应=0) / off16 LSN
xxd -s $((16384-16)) -l 16 -g 4 "$F"     # 页尾：off16376 chksum2 / off16380 LSN尾4B
# 判读：off22-25 应 == off16380-16383（不等=R2 torn）；chksum1/chksum2 是否同时为 0
```

**D2. 全文件健康扫描（区分首页孤发 vs 全局损坏）**
```bash
innochecksum "$F"          # XtraBackup 发行版自带（源码 utilities/innochecksum.cc）
# 仅 page0 报错 → 首页局部问题；多页报错 → 存储级损坏(R1)，升级硬件排查
```

**D3. 瞬态性验证（判 R9/R2 瞬态）**
```bash
# 重跑一次单库/单表备份，观察同一文件是否再报错
xtrabackup --backup --target-dir=/tmp/retry_bk --databases=usercdb ... 2>&1 | grep -c 'Checksum mismatch'
# 再报 → 稳定损坏走 D1/D2；不再报 → 瞬态（R9 窗口冲突或 R2 瞬态），对齐分区任务调度时间
```

**D4. 配置核对（判 R4）**
```bash
mysql -NBe "SELECT @@innodb_checksum_algorithm"   # 默认 crc32；若 strict_* 且实例跨版本升级过 → R4
```

**D5. 文件完整性（判 R6）**
```bash
stat -c %s "$F"; N=$(( $(stat -c %s "$F") / 16384 )); echo $(( $(stat -c %s "$F") - N*16384 ))
# 余数非 0 → 文件截断/junk 尾
```

**D6. 加密/压缩分支（通用场景；本案 Flags 已排除）**
```bash
mysql -NBe "SELECT CREATE_OPTIONS FROM information_schema.tables WHERE table_schema='usercdb' AND table_name LIKE 'ur_usergoods_info_his%'"
# 出现 ENCRYPTION='Y' → 检查 keyring 插件与 master key 轮换历史(R3)
# 出现 ROW_FORMAT=COMPRESSED → 用 innochecksum 关注 zip 校验输出(R5)
```

### F8. 文案辨析：同内核不同文案（对应 AC-6）

| 场景 | 日志文案 | 入口 |
|------|---------|------|
| 打开/扫描表空间（本案） | `Checksum mismatch in datafile: ...` | validate_first_page |
| backup 逐页复制 | `Database page corruption detected at page N, retrying...` → 10 次后 `failed to read page after 10 retries. File ... seems to be corrupted.` | xb_fil_cur_read（xtrabackup/src/fil_cur.cc:386-414），失败重试 10 次×100ms |
| copy-back 重加密 | ut_a 断言崩溃 | backup_copy.cc:861 |
| mysqld 启动/运行 | 各自 ER 消息 | buf0buf.cc 读页路径 |

现场据此分诊：看到"retrying..."是复制阶段逐页问题（有 doublewrite 保护语义），
看到"in datafile"是打开阶段首页问题（**直接导致缺文件**，更严重）。

## 结论与建议

1. **报错本质**：backup 启动扫描阶段对该分区首页的只读校验失败；
   校验失败使该表空间未能注册，**该分区不会进入备份集，且备份照常成功结束**——
   这是静默的数据完整性风险，比报错本身严重。
2. **本案主因排序**：R9（分区维护窗口冲突）≈ R2（torn 态被扫到）> R1（真实损坏）；
   keyring/压缩/算法配置已由 Flags=16417 解码排除。
3. **处置建议**（按序）：
   a. 立即用 D0 确认既有备份是否缺失该分区，缺失则尽快补备该库；
   b. 用 D1-D3 判定瞬态 or 稳定损坏；瞬态 → 将分区维护任务调度避开备份窗口；
   c. 稳定复现 → D2 全文件扫描定位损坏范围，评估 `CHECK TABLE` / 重建分区修复；
   d. 中长期：备份脚本增加"报错后核对 xtrabackup_tablespaces 与实际文件一致性"
      的后置检查，把静默缺文件变成显式失败（可作为后续 bugfix 任务立项）。
4. **遗留假设**（无法在本仓库内闭环，已标注置信度）：R8 GoldenDB 定制偏差（低，
   无 git 历史可比对）；存储层故障细节（低，需现场硬件日志佐证）。

## 参考资料

- storage/innobase/fsp/fsp0file.cc:552-665 —— validate_first_page 与报错拼接
- storage/innobase/buf/checksum.cc:274-495, 571-708 —— is_corrupted 判定内核
- storage/innobase/include/fsp0types.h:230-354 —— flags 位布局宏
- storage/innobase/include/fil0types.h:42-115 —— 页内字段偏移常量
- storage/innobase/fil/fil0fil.cc:11718-11800, 2344-2351 —— fil_open_for_xtrabackup/open_ibds
- storage/innobase/xtrabackup/src/xtrabackup.cc:496-509, 2259-2283, 3252-3305 —— 扫描与拷贝枚举
- storage/innobase/xtrabackup/src/fil_cur.cc:251-425 —— 逐页复制与重试
- storage/innobase/handler/ha_innodb.cc:21379-21402 —— innodb_checksum_algorithm 默认 CRC32
- evidence/prod-error-log.txt —— 生产报错原文
