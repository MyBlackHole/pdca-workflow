# XtraBackup "Checksum mismatch in datafile" 排障知识

来源：T0389 根因分析（2026-08-24），基准 percona-xtrabackup-8.0.25-17 源码树。

## 1. 一句话结论

backup 启动扫描阶段对 .ibd **首页**的校验失败 → 该表空间未注册进 fil_system →
**该文件不会被复制进备份集**，但备份照常成功结束（报错被忽略）——
这是**静默数据丢失风险**，不是无害告警。

## 2. 因果链（每跳可验证）

```
validate_first_page 失败(fsp0file.cc:638 报错)
→ fil_open_for_xtrabackup 提前 return(fil0fil.cc:11733-11735)
→ fil_space_create/fil_node_create 未执行(fil0fil.cc:11760+)
→ datafiles_iter_new 只遍历 fil_system(xtrabackup.cc:496-509)
→ 该 .ibd 缺席备份集; open_ibds 忽略返回值故无 error(fil0fil.cc:2344-2351)
```

## 3. 文案辨析（同判定内核不同入口）

| 文案 | 入口 | 后果 |
|------|------|------|
| `Checksum mismatch in datafile` | 打开/扫描首页 | **该文件缺席备份集** |
| `Database page corruption detected at page N, retrying...` | 逐页复制(重试10次) | 重试失败才中止 |
| copy-back 断言崩溃 | backup_copy.cc:861 ut_a | 恢复阶段失败 |

## 4. Flags 快速解码

Flags 位布局（fsp0types.h）：bit0 POST_ANTELOPE / bits1-4 ZIP_SSIZE /
bit5 ATOMIC_BLOBS / bits6-9 PAGE_SSIZE / bit13 ENCRYPTION / bit14 SDI。
例：16417(0x4021)=DYNAMIC+16K+非压缩+未加密 → 直接排除 keyring/压缩类根因。

## 5. 排查决策树（命令可直接执行）

```bash
# D0 影响面(最优先): 该分区是否进了备份集?
find <backup_dir> -name '<file>.ibd'; grep '<name>' <backup_dir>/xtrabackup_tablespaces
# 物理缺失而元数据在 → 备份不可恢复此分区, 立即补备

# D1 首页复核: torn 判定(off22-25 应== off16380-16383)
xxd -l 40 -g 4 <f>.ibd; xxd -s $((16384-16)) -l 16 -g 4 <f>.ibd

# D2 全文件扫描: 仅page0报错=局部; 多页=存储级损坏
innochecksum <f>.ibd

# D3 瞬态性: 重跑不再报=分区维护窗口冲突或瞬态torn
# D4 SELECT @@innodb_checksum_algorithm   (默认crc32, strict_* 才会暴露算法混用)
# D5 stat 文件大小 % 页大小 != 0 → 截断/junk尾
# D6 CREATE_OPTIONS 含 ENCRYPTION/COMPRESSED 时走 keyring/zip 子路径
```

## 6. 易踩坑

- 全零首页被豁免（DB_PAGE_IS_BLANK 放行，fil0fil.cc:11729），能报此错的必是非零损坏页。
- xtrabackup_tablespaces 元数据来自 I_S.FILES，与实际拷贝列表来源不同——
  元数据有 ≠ 文件在，核对必须以物理文件为准。
- 分区表活跃年分区（如 #p#p2026）与分区维护/归档任务时间重叠是高频诱因；
  瞬态报错应对齐调度窗口而非急修存储。

## 7. 对后续备份的影响（2026-08-24 补充）

- 进程能力零影响：open_ibds 忽略单文件失败，每 space 独立注册，下次 backup
  重新扫描全部文件。
- 瞬态根因下次自愈；稳定损坏则每个备份周期持续静默丢同一分区。
- **增量链断裂**：--incremental 同走 datafiles_iter_new(xtrabackup.cc:4034)。
  全量缺文件 + 后续增量校验通过产生 .delta → --prepare --incremental-dir
  时 base 无对应 .ibd → 整条增量链不可恢复。周期全量+增量策略下必须先修 base。
- 假自愈：DROP PARTITION 后报错消失 ≠ 修复，历史受损备份仍不可恢复该分区。

## 8. backup 主流程图与问题位置（2026-08-24 补充）

### 8.1 主流程（★=问题位置）

```
xtrabackup --backup
  ▼
① 初始化+打开 ibdata (xb_load_tablespaces; HOTBACKUP 下 ibdata 首页校验不编译)
  ▼
② 扫描全部 .ibd 逐个打开注册 (open_ibds→fil_open_for_xtrabackup)
     ★1 首页校验失败→打印报错(fsp0file.cc:638)
     ★2 提前return未注册(fil0fil.cc:11733)
     ★4 返回值被忽略→备份继续(fil0fil.cc:2344)
  ▼
③ 元数据收集(I_S.FILES 独立来源, xtrabackup.cc:3995)
  ▼
④ redo 拷贝线程("log scanned up to")
  ▼
⑤ 并行逐页拷贝(datafiles_iter_new:496)
     ★3 只遍历已注册清单→缺席文件被跳过
     页级失败走另一文案"corruption detected at page N"+重试10次
  ▼
⑥ 写元数据→completed OK!(无error→看似成功)
```

### 8.2 首页判定决策流

```
读 page0 ─┬─ IO失败→"Cannot read first page"
          ├─ 全零→豁免放行(redo后补)
          ├─ flags/page_no/space_id异常→各自文案
          └─ is_corrupted(): 加密未解密/torn/checksum不匹配
                 任一命中→★"Checksum mismatch in datafile"
              全过→注册→进入拷贝
```

图例：▼ 流程方向；★ 报错相关位置；├└ 决策分支

## 9. R9 表述精炼（2026-08-24 二次追问后修正）

原报告将 R9 表述为"分区维护窗口冲突"，经用户质询后精确化：

- 原子 DDL 保护字典/binlog/崩溃恢复一致性，**不保护物理文件对旁路进程的可见性**——
  REORGANIZE 的新 .ibd 自 create 起即对目录扫描裸露。
- 但 --lock-ddl 默认 on（xtrabackup.cc:955 def=1），且时序为先获锁后扫描
  （xb_init:7595 → LOCK INSTANCE FOR BACKUP:6979 → 扫描:3998）；
  该锁等待活跃 DDL 结束并阻塞后续 DDL → **默认配置下扫描期并发 DDL 理论不存在**。
- R9 真实窗口收窄为三条件：① 生产显式关闭(--no-lock/--lock-ddl=false,:6892)；
  ② 锁只挡 DDL 不挡 DML——普通刷脏 torn 态(R2)无需 DDL 即可撞上；
  ③ 结构性弱点不变：扫描路径零重试 vs 拷贝路径 10 次重试(fil_cur.cc:313)。
- 排查第一动作改为：核对生产备份命令行是否含 --no-lock/--lock-ddl=false，
  一票裁决 R9 窗口是否全开。

图例：无（文字节）

## 10. 深度问答附录索引

五轮追问（影响本次/后续备份、首页限定性、流程图与4个问题位置、R9机理、
原子DDL边界、零重试 vs mysqld三层容错）的完整代码证据已汇总至：
records/T0389-0824-checksum-mismatch-datafile/appendix-followup-analysis.md
核心速记：扫描零重试(fil0fil.cc:2344,11733) vs 拷贝10次重试(fil_cur.cc:313)；
mysqld 三层兜底——ibdata retry×2+dblwr恢复(fsp0sysspace.cc:552)、
页级dblwr修复(buf0dblwr.cc:2193)、新页豁免(buf0buf.cc:5620)，
三者均 #ifndef UNIV_HOTBACKUP，xtrabackup 进程内不可用。
