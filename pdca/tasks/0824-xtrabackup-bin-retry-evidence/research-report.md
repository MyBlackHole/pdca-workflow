# 取证报告：GoldenDB 部署二进制 xtrabackup 的 validate_first_page 处理与重试逻辑

任务：T0393 | 场景：research | 分析对象：`/home/black/Downloads/goldendb-xtrabackup/xtrabackup`
文件属性：ELF 64-bit **aarch64**，787,845,856 字节，dynamically linked，
**with debug_info, not stripped**（符号级取证可行）
对照基线：Percona 官方源码 percona-xtrabackup-8.0.25-17（T0389 结论）

## 调研目标

部署的 GoldenDB 二进制是否处理了 validate_first_page 校验问题？
是否实现了重试逻辑？给出二进制级证据。

## 方法

1. `nm -n` 导出 135,209 个符号建立地址索引（/tmp/opencode/syms.txt）；
2. `strings -a` 提取版本与消息串；
3. `aarch64-linux-gnu-objdump -d --start-address/--stop-address` 定向反汇编
   6 个关键函数；
4. 解析 bl 调用目标→符号名映射，统计调用计数；甄别回边目标内容区分
   真循环与共享错误出口。

复现命令模板：
```bash
nm -n xtrabackup > syms.txt
aarch64-linux-gnu-objdump -d --start-address=0x1422100 \
  --stop-address=0x14247c8 xtrabackup
```

## 发现

### F1. 来源鉴定：GoldenDB 定制构建，基线 8.0.25

- 版本串 "8.0.25"；运行时路径 `$ORIGIN/../lib/gdblib`；
- 构建机路径 `/root/db-tool/.../DB-TOOL/xtrabackup/storage/innobase/...`；
- 大量 `[gdb]` 前缀定制日志（进度百分比、copy_back 等）。
- **注意**：本地源码树为 Percona 官方 tarball，与该二进制非同源；
  二进制中的定制无法从本地源码逐行对应。

### F2. 核心答案：用户 .ibd 扫描路径仍是零重试

`fil_open_for_xtrabackup`（0x1409de0）调用序列与上游同构：

```
set_name → set_filepath → open_read_only(:1409e94)
→ [失败] Datafile::shutdown → return
→ validate_first_page(:1409ed8)      ← 仅此一次
→ [失败] shutdown → return           ← 无重试分支
→ fil_space_get / os_file_get_size / fil_space_create / fil_node_create
```

函数内大回边仅 5 个且均为错误出口共享块（0x1409ea4×4 等）。
其调用者 `Tablespace_files::open_ibds`（0x140a118）在遍历循环
（回边 0x140a1f0/0x140a1a8）内直呼 fil_open_for_xtrabackup（:140a244），
**循环体内无任何 retry 结构**——上游"一枪毙命"行为原样保留。

### F3. validate_first_page 本体：无内部重试（与上游一致）

函数区间 0x1422100-0x14247c8（9928B）。关键调用计数：

| 被调函数 | 次数 | 地址 |
|----------|------|------|
| Datafile::read_first_page | **1** | 0x1422710 |
| fsp_is_checksum_disabled | 1 | 0x142296c |
| BlockReporter::is_corrupted | **1** | 0x14229f4 |
| Datafile::restore_from_doublewrite | **0** | — |
| Datafile::free_first_page | 4（错误出口） | 0x142242c 等 |

90 个 ≥128B 回边聚类后最大簇仅 6 条，目标为 ios_base/logger 初始化、
free_first_page 等**共享清理/日志出口**，非循环头——单次读取+单次判定的
线性结构与上游一致。

**附带发现**：尾部 0x142458c-0x1424794 密集调用 `OSDecodeAES(char*&, char const*)`
×8——GoldenDB 私有密钥解码函数（推测国密改造），证实二进制含大量上游不存在的修改。

### F4. 定制点实锤：ibdata 路径编入了 retry×2 + doublewrite 恢复

上游源码中 `SysTablespace::read_lsn_and_check_flags` 被
`#ifndef UNIV_HOTBACKUP`（fsp0sysspace.cc:525→941 同一条件块）排除——
**官方 xtrabackup 二进制不应包含它**。GoldenDB 二进制中：

- 符号存在（0x142e810，1080B）；
- 内部结构完整还原：

```
0x142e848 read_first_page(#1)        ┐
0x142e89c validate_first_page(#1)    │ retry 循环
0x142e878 read_first_page(#2)        │ 回边 → 0x142e854
0x142e8f0 validate_first_page(#2)    ┘ 对应上游 for(retry=0;retry<2;)
0x142e8b4 restore_from_doublewrite   ← 首次失败时从 dblwr 找 page0 副本
0x142e8c4 close                       （对应上游 :552-561）
```

- 可达性：`xb_load_tablespaces`(0xd95b18) 调用 `check_file_spec` 与
  `SysTablespace::open_or_create`（0x142ed40），后者含 **2 处直接 bl**
  read_lsn_and_check_flags（0x142f290 / 0x142f2d0，参数 this+flush_lsn，
  返回值 cmp #0xa 即 DB_SUCCESS 判定）；backup 参数
  open_or_create(create_new_db=false, flush_lsn≠null) 满足执行条件。

**作用域限定**：该路径仅覆盖系统表空间 ibdata 第一文件的 page 0
（上游 ut_ad(space_id()==TRX_SYS_SPACE)）。用户分区 .ibd 不经过此路径。

### F5. 拷贝路径 10 次重试保留

`xb_fil_cur_read`（0xda8ef8）：os_file_read_no_error_handling×2
（首读 0xda90b8 + 重读 0xda9358）、is_corrupted（0xda927c）、
msg 输出（"corruption detected ... retrying"）、read_retry 回边
（→0xda904c，io_throttling 处）等 17 条函数内回边构成重试循环——
与上游 fil_cur.cc:313/386-413 一致。

### F6. 六函数判定总表

| 函数 | 地址 | 重试结构 | doublewrite 恢复 | 与上游差异 |
|------|------|---------|------------------|-----------|
| validate_first_page | 0x1422100 | 无（线性） | 无调用 | 尾部新增 OSDecodeAES×8 |
| fil_open_for_xtrabackup | 0x1409de0 | 无 | 无 | 基本一致 |
| Tablespace_files::open_ibds | 0x140a118 | 无（遍历≠重试） | 无 | 混入 st_persist_var/fil_assign_new_space_id 定制 |
| SysTablespace::read_lsn_and_check_flags | 0x142e810 | **retry×2** | **restore_from_doublewrite** | **上游 HOTBACKUP 排除，GoldenDB 编入** ★ |
| SysTablespace::open_or_create | 0x142ed40 | — | 调用上者×2 | 上游 HOTBACKUP 排除，GoldenDB 编入 ★ |
| xb_fil_cur_read | 0xda8ef8 | 10 次×100ms | 无 | 一致 |

## 结论与建议

1. **主问题答案**：部署二进制**没有**改变用户表空间 .ibd 的首页校验行为——
   扫描路径依旧零重试、校验失败即静默放弃该文件。T0389 的结论
   （静默缺文件风险、D0-D6 排查决策树）对生产二进制**完全适用**。
2. **定制实际做了什么**：把 mysqld 启动专用的 ibdata 首页容错
   （retry×2 + restore_from_doublewrite）编入了 backup 流程——
   但只惠及 ibdata，不覆盖用户分区表空间。
3. **对本案（p2026 分区报错）的含义**：无论跑官方版还是本定制版，
   该分区都会以同样方式缺席备份集；升级/更换此二进制不能解决问题。
4. **建议**：维持 T0389 附录的行动清单；如需真正修复，
   需在 fil_open_for_xtrabackup/open_ibds 层增加重试或 dblwr 兜底
   （可参考 read_lsn_and_check_flags 的现成模式）——建议作为独立 bugfix 任务立项。

## 参考资料

- 反汇编产物：/tmp/opencode/{vfp,ofxb,openibds,rlacf,fcr}.asm
- 符号索引：/tmp/opencode/syms.txt（nm -n 导出）
- 对照源码：storage/innobase/fsp/fsp0file.cc、fsp/fsp0sysspace.cc、
  fil/fil0fil.cc、buf/buf0dblwr.cc、xtrabackup/src/fil_cur.cc
- 关联任务：T0389（源码级根因分析，archive/2026-08）
