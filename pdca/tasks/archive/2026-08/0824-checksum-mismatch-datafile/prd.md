# 分析 XtraBackup Checksum mismatch in datafile 原因

## 问题陈述

在 Percona XtraBackup 8.0.25-17（GoldenDB 定制源码树）执行 `xtrabackup --backup`
期间出现 `Checksum mismatch in datafile` 报错，需要根因分析：错误的精确产生位置、
判定逻辑全部分支、backup 阶段的触发链路、以及所有可能的物理根因与可执行排查手段。

## 方案概述

产出一份根因分析结论文档（conclusion.md），内容组织为：

1. **代码机制层**：报错拼接点与判定内核（is_corrupted 全部分支）；
2. **触发链路层**：--backup 阶段从启动到报错的完整调用链，及与逐页复制链的关系；
3. **根因假设层**：≥8 个根因假设，每条映射到代码证据与现场观测特征；
4. **排查决策树**：以 backup 阶段为主入口的诊断命令序列
   （innochecksum / hexdump 关键偏移 / keyring 检查 / 存储层检查），
   加密与压缩表空间分支（R3/R5）纳入重点（用户环境未知）。

## 已验证的代码事实（claim verification）

### 错误消息拼接点

- `"Checksum mismatch"`：storage/innobase/fsp/fsp0file.cc:638；后缀
  `" in datafile: <path>, Space ID: <id>, Flags: <flags>."`：fsp0file.cc:657。
- 所在函数 `Datafile::validate_first_page()`（fsp0file.cc:552），仅校验表空间**第一页**。
- 直接触发条件：`BlockReporter::is_corrupted()` 返回 true（fsp0file.cc:633-639）。

### --backup 阶段触发链（用户确认的场景）

```
xtrabackup --backup
 └─ xb_load_tablespaces()                      [xtrabackup.cc:3252]
     ├─ srv_sys_space.check_file_spec()        [xtrabackup.cc:3265]   仅查文件规格，不做页校验
     ├─ srv_sys_space.open_or_create()         [xtrabackup.cc:3273]   打开 ibdata
     │    （read_lsn_and_check_flags 内的 validate_first_page 在 UNIV_HOTBACKUP
     │      下不参与编译 —— fsp0sysspace.cc:525 条件编译排除）
     └─ xb_scan_for_tablespaces()              [xtrabackup.cc:2259]
         └─ fil_scan_for_tablespaces(true)
             └─ fil_open_for_xtrabackup(path)  [fil0fil.cc:11718]
                 └─ Datafile::validate_first_page(SPACE_UNKNOWN,...) [fil0fil.cc:11727]
                     └─ is_corrupted()==true → "Checksum mismatch in datafile"
```

- 关键豁免：`fil_open_for_xtrabackup` 对返回 `DB_PAGE_IS_BLANK`
  （Header page consists of zero bytes）的文件放行——注释明确
  "allow corrupted first page ... restore from redo log later"（fil0fil.cc:11730-11733）。
  因此**全零首页不会报本错误，能报出来的是非零但校验失败的首页**。
- 后续外部表空间同样经 `fil_open_for_xtrabackup`（xtrabackup.cc:3302-3305）。

### 判定内核全部分支（storage/innobase/buf/checksum.cc:285 起）

1. 加密页类型识别失败即判损坏（FIL_PAGE_ENCRYPTED 等，:274-280、292-294）。
2. Torn page：页内 FIL_PAGE_LSN+4 与页尾 +4 处 4 字节不一致（:296-305）。
3. 算法 NONE 或 skip_checksum 短路放行（:311-314）。
4. 压缩页走 verify_zip_checksum（:316-318、571-708）。
5. 双字段校验：页头 checksum 字段与页尾字段须通过 CRC32（含 legacy big-endian
   回退）/ InnoDB 新旧公式 / BUF_NO_CHECKSUM_MAGIC 兼容链之一（:364-491）。
6. 空页豁免：三字段全零 + 整页零检查；UNIV_HOTBACKUP 编译下跳过逐字节复核循环
   （:330-353，条件编译 :335-351）。
7. xtrabackup 编译下 buf_page_lsn_check 为空操作（:164 条件编译）——
   只做页内 LSN 自洽检查，不对照 redo checkpoint LSN。

### 共用判定内核的其他路径（区分文案避免误导）

| 路径 | 文案 |
|------|------|
| backup 逐页复制 xb_fil_cur_read（fil_cur.cc:386-414） | `Database page corruption detected at page N, retrying...`，10 次重试失败后 `failed to read page after 10 retries` |
| copy-back 重加密断言（backup_copy.cc:861） | ut_a 断言崩溃 |
| mysqld 启动/运行读页（buf0buf.cc:5609+） | 各自 ER 消息 |

## 生产案例证据（evidence/prod-error-log.txt）

```
260814 19:00:42 >>log scanned up to (12888113898220)
Checksum mismatch in datafile: ./usercdb/ur_usergoods_info_his_06#p#p2026.ibd,
Space ID:520513, Flags:16417.
```

案例解码结论（Do 阶段需复核并写入结论文档）：

- Flags=16417 (0x4021) 按 fsp0types.h 位布局解码：
  POST_ANTELOPE=1、ATOMIC_BLOBS=1（DYNAMIC 行格式）、ZIP_SSIZE=0（非压缩）、
  PAGE_SSIZE=0（16K 页）、ENCRYPTION=0（未加密）、SDI=1。
  → **排除 R3(keyring)/R5(压缩页)** 为本案主因。
- 文件为分区表单分区（`#p#p2026`），历史表活跃年份分区，
  backup 运行时大概率正被业务/分区维护任务写入。
- 报错与 `log scanned up to` 同秒出现，确认发生在 --backup 运行期。
- 行为后果（已验证代码路径）：`Tablespace_files::open_ibds()`
  （fil0fil.cc:2344-2351）与外部文件循环（xtrabackup.cc:3302-3305）
  调用 `fil_open_for_xtrabackup` 均**忽略返回值** → 备份继续；
  但若该 space 未注册进备份集，备份集可能缺失该分区文件，
  恢复后该分区不可访问 —— 结论文档必须给出"如何确认该分区是否进入备份集"的检查方法
  （xtrabackup_tablespaces 元数据 / backup 目录文件存在性）。

## 根因假设清单

| # | 根因 | 代码依据 | 现场观测特征 |
|---|------|---------|-------------|
| R1 | 首页真实损坏（磁盘坏块/存储故障/手工改动） | 双字段校验失败 | hexdump 见异常字节模式；innochecksum 全文件扫描多页报错 |
| R2 | 半页写入 torn write（掉电/崩溃遗留；或 backup 扫描瞬间读到未落盘完整的首页） | LSN 尾部比对失败 | 页尾 4 字节与 FIL_PAGE_LSN+4 不一致；重跑 backup 报错消失则为瞬态 |
| R3 | 加密表空间 master key 缺陷致解密失败判损坏 | 加密页类型分支 | 本案 ENCRYPTION=0，**已排除为主因**，保留为通用分支 |
| R4 | innodb_checksum_algorithm 过严（strict_*）与写入方算法不匹配 | 兼容回退仅非 strict 静默接受 | my.cnf strict_* 配置；换非 strict 后消失 |
| R5 | 压缩表页 zip 校验失败 | verify_zip_checksum | 本案 ZIP_SSIZE=0，**已排除为主因**，保留为通用分支 |
| R6 | 文件截断/junk 尾导致页边界错位 | fil_cur.cc:296-309 junk 处理对照 | 文件字节数非页大小整数倍 |
| R7 | 版本混用 legacy 校验和 | legacy big-endian / old innodb 分支 | 跨大版本升级过的实例 |
| R8 | GoldenDB 定制改动引入的偏差 | 待 Do 阶段 diff 上游 v8.0.25 核对 | 定制 patch 与上游行为差异 |
| R9 | 分区维护窗口冲突：ADD/REORGANIZE/REBUILD PARTITION 或归档任务重建该分区期间扫描到中间态首页 | open_ibds 扫描时机 vs DDL 窗口 | 报错时间与分区任务调度时间重叠；重跑即恢复 |

## 验收标准

- [ ] AC-1: 结论文档给出报错拼接点的文件与行号区间，且在本仓库运行 `grep -rn "Checksum mismatch"` 可复现定位。
- [ ] AC-2: 结论文档列出判定内核全部分支（≥5 类），每类附 checksum.cc 行号证据。
- [ ] AC-3: 结论文档包含 --backup 阶段完整调用链（从 xb_load_tablespaces 到 validate_first_page），并说明 DB_PAGE_IS_BLANK 豁免与 UNIV_HOTBACKUP 条件编译差异。
- [ ] AC-4: 结论文档给出 ≥8 个根因假设（R1-R8 覆盖），每条附代码依据与现场观测特征。
- [ ] AC-5: 结论文档提供按决策树组织的诊断命令序列（innochecksum、hexdump 关键偏移、keyring 检查），每条命令可直接复制执行且注明预期输出含义；加密/压缩分支（R3/R5）有独立子路径。
- [ ] AC-6: 结论文档区分"精确文案的首页校验路径"与共用内核的其他路径（逐页复制/copy-back/mysqld 启动）各自文案，防止现场误判。
- [ ] AC-7: 结论文档对生产案例（ur_usergoods_info_his_06#p#p2026.ibd, Flags=16417）完成逐字段解码，给出本案根因的优先级排序结论与验证步骤。
- [ ] AC-8: 结论文档说明报错后 backup 的实际行为（open_ibds 忽略返回值、备份继续），并给出"该分区是否进入备份集"的确认方法（xtrabackup_tablespaces/备份目录检查）与缺失时的补救建议。

## Seam 分析（research 场景无测试产物）

### 声明的测试接缝
- seam: （research 场景，无自动化测试产物；验收以结论文档中可复现的 grep 与命令序列为准）
