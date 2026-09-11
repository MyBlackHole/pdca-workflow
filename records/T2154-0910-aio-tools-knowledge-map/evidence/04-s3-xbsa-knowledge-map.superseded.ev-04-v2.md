# S3 与介质扩展 Knowledge Map（知识地图）

> **文档定位**：本文是对象存储与第三方介质子系统的导航—— **「介质能力 → 代码位置 → 对外契约」**，以及全仓最重要的 **孤岛清单**：哪些模块仓内零引用、引用即错。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；`file:line` 行号易变动，以符号名为准
> **适用分支**：6.2.0.0（目录 `6200/release`），实证 commit `fe9d4364`
> **最后更新**：2026-09-10

---

## 1. 模块组织总览

| 目录 | 职责 | 关键文件 |
|---|---|---|
| `s3-tool/` | 通用 S3 搬运二进制 `s3-tool`：upload/download/list/S3→S3，并发线程池 | `s3-tool/main.cpp:76`，`s3-tool/s3-service.h:50`，`s3-tool/obs-service.h:42`，`s3-tool/s3-command.h:38` |
| `s3tools/` | S3 快照/文件套件：s3file（文件 + ZFS 快照上传）+ s3mount（FUSE 挂载） | `s3tools/s3file/main.cpp:396`，`s3tools/s3mount/fuse.cpp:222`，`s3tools/libs/xmake.lua:2` |
| `huanweicloun-sdk-s3-data-backup/` | ZFS 快照 → S3 备份/挂载：afsd（FUSE 守护）/ afs-cli 客户端 | `my-fuse/fuse.cpp:71`，`my-fuse/afs-cli.cpp:136`，`README.md:1` |
| `xbsa/` | XBSA 共享库 + data/xlog 文件解析工具 | `xbsa/src/xbsa/xbsa.h:219`，`xbsa/src/xbsa/xbsa.c:67`，`xbsa/src/main.c:324`（解析器），`xbsa/src/rch/rch.h:166`，`xbsa/src/xlog/xlog.h:62` |
| `libobk/` | Oracle 风格 SBT 库 + FileTransferAgent（`:12000`） | `libobk/include/libobk.h:21`，`libobk/lib/sbt/libobk.c:207`，`libobk/main.c:49`，`libobk/simulator/main.c:121` |
| `dmsbtex/` | 达梦 SBT 扩展库 + dm-ftp（`:1255`） | `dmsbtex/dmsbt_dll.h:223`，`dmsbtex/sbt.c:118`，`dmsbtex/main.c:100`，`dmsbtex/protocol.h:27` |
| `bwlimit/` | 令牌桶限速库 + 管理工具（**现行**，被 rpc 反向依赖） | `bwlimit/lib/bandwidth.h:33`，`bwlimit/lib/bandwidth.c:50`，`bwlimit/lib/shm_comm.c:13`，`bwlimit/main.c:14` |

> **一句话记忆**：bwlimit 是「自己人（被 rpc 用）」，其余六个是「对外交付、仓内无人用」——动它们之前先读 §6 孤岛清单。

---

## 2. 能力总览（能力 → 代码 → 使用方）

| 能力 | 解决什么问题 | 核心代码位置 | 主要入口 | 使用方 |
|---|---|---|---|---|
| **S3 对象上传/下载/列举** | 本地 ↔ S3，S3 ↔ S3 迁移 | `s3-tool/s3-service.h:63`；`s3tools/libs/s3-service.*`（同构） | `s3-tool/main.cpp:76` → `UploadFileToS3:313/ListFileFromS3:430/DownloadFileFromS3:493`；`s3file/main.cpp:396` → `local_to_s3:481/s3_to_local:696` | ⚠️ 仓内零调用（仅 `s3file/main.cpp:425` 字符串 `InitApi("s3-tool")`，无链接依赖） |
| **ZFS 快照流式上 S3/合并/国密** | 全量 + 增量快照分块、父块合并、SM4 | `s3tools/s3file/main.cpp:867`（`upload_snapshot_bundle_to_s3`），`:1222`（`upload_snapshot_to_s3`） | s3file 子命令 `get/up/rm/upload-snapshot/check-snapshot/destroy-snapshot`（`main.cpp:175`） | 除自身外调用者无法确认（缺跨仓证据） |
| **FUSE 挂载 S3 文件/快照卷** | S3 对象暴露为本地文件系统/XFS 卷 | `s3tools/s3mount/fuse.cpp:318`（`fuse_main`）；`my-fuse/fuse.cpp:147`（afsd 同构） | s3mount（`mount-file/mount-snapshot`，`fuse.cpp:178`）；afsd（`my-fuse/fuse.cpp:71`） | `fsclient/cli_help.cpp:12` 仅帮助文本提及 "from afsd"，无 `add_deps` 链接实证——疑似运行时协作 |
| **XBSA 备份/查询/恢复** | 给备份软件提供标准磁带 API | `xbsa/src/xbsa/xbsa.c:67`（`BSAInit`），`:120`（`BSACreateObject`），`:281`（`BSAQueryObject`），`:513`（`BSAGetObject`） | 库直接导出；demo（`demo.c:29`）；解析器（`main.c:324` → `data_process/xlog_process`） | ⚠️ 仓内零使用方（仅 xmake/version） |
| **Oracle-SBT2 备份通道** | OceanBase/RMAN 式备份 | `libobk/lib/sbt/libobk.c:207`（`sbtinit2`），`:265`（`sbtbackup`），`:527/497`（`sbtwrite2/sbtread2`），`:567`（`sbtrestore`） | `test.c:39` 范式；`simulator/main.c:121` 函数指针装载 | ⚠️ 仓内零使用方 |
| **达梦 DMSBT 2.1 备份通道** | 达梦数据库第三方介质备份 | `dmsbtex/sbt.c:118`（`sbtversion`），`:124/167`（`sbtinit/sbtinit2`），`:320/383`（`sbtbackup/sbtwrite`），`:516/579`（`sbtrestore/sbtread`） | 达梦服务端 dlopen 调用；dm-ftp（`main.c:100` → `startWorker:282` → `_worker:197`） | ⚠️ 仓内零使用方 |
| **跨进程限速** | RPC 上传/下载限速整形 | `bwlimit/lib/bandwidth.c:50`（`bandwidth_init`），`:120`（`bandwidth_limit`）；`shm_comm.c:13`（SHM 共享） | `main.c:14` 多子命令；数据面 `bandwidth_limit` | ✅ 强实证：`rpc-io.cpp:107`（DOWNLOAD），`:183`（UPLOAD）；`rpc/main.cpp:378`（`RPC_SERVER_ID`）；`rpc-client.cpp:640`（`CLIENT_ID`） |

---

## 3. 核心任务链

### 3.1 s3-tool

```
main:76 → args_process → S3Service::InitApi
  → UploadFileToS3:313（dir_traversal_2 + create_thread UploadObjectToS3Thread:680 → UploadObject）
  → ListFileFromS3:430（ListObject）→ StopApi
```

### 3.2 s3file

```
main:396 → s3file_init_config → argp_parse（子命令）
  → S3Service::InitApi("s3-tool")
  → local_to_s3:481（thread_pool_init + post upload_thread:241）
  → upload_snapshot_to_s3:1222（zfs_stream_begin → bundle_block_proc → post upload_snapshot_bundle_to_s3:867 → PutObject）
```

### 3.3 s3mount / afsd

```
main（s3mount/fuse.cpp:222）→ s3mount_init_config → ObsService::InitSDK:258
  → new S3Service → init_s3_filesystem → init_operations → fuse_main:319
afsd 同构（my-fuse/fuse.cpp:71,94,147）
```

### 3.4 xbsa 解析器 / 库

```
解析器 main:324 → args_process → traverse_directory → thread_pool_init
  → data_process:221（rch_check_file_name → post do_data_process:189 → rch_parse）
  → xlog_process:251（→ do_xlog_process:209 → xlog_parse）
库：BSAInit（xbsa.c:67）→ BSACreateObject:120（BSASendData）→ BSAQueryObject:281 → BSAGetObject:513（BSAGetData）
```

### 3.5 libobk

```
FileTransferAgent（main.c:49）→ select/accept → startWorker:156
库：sbtinit2:207 → sbtbackup:265 → sbtwrite2:527 / sbtread2:497 → sbtclose2:308 → sbtend:343（api 表 :628-638 装配）
```

### 3.6 dmsbtex（dm-ftp 私有协议）

```
main.c:100 → start_server(:1255) → accept → startWorker:282 → _worker:197 recv_packet
  → switch CMD_BACKUP_OPEN / BACKUP / CLOSE / CMD_RESTORE_*（protocol.h:27-38）
  → OnBackupOpen:302（open 本地文件）/ OnBackup:365（write）/ OnRestore:479（read + send_packet）
```

---

## 4. 对外契约（逐字摘录）

- **XBSA 标准接口**（`xbsa/src/xbsa/xbsa.h:219-250`）：`BSABeginTxn` `BSACreateObject` `BSADeleteObject` `BSAEndData` `BSAEndTxn` `BSAGetData` `BSAGetEnvironment` `BSAGetLastError` `BSAGetNextQueryObject` `BSAGetObject` `BSAInit` `BSAQueryApiVersion` `BSAQueryObject` `BSAQueryServiceProvider` `BSASendData` `BSATerminate`；共享库 target `xbsa64`（`set_kind("shared")`）。
- **达梦 SBT**（`dmsbtex/dmsbt_dll.h:223-380`）：`sbtversion` `sbtinit` `sbtinit2` `sbtbackup` `sbtwrite` `sbtclose` `sbtinfo` `sbtend` `sbtrestore` `sbtread` `sbterror` `sbtcommand` `sbtdelete`；`dmsbtex` shared + `dm-ftp` binary（私有协议 `CMD_BACKUP_OPEN 0x1000` / `CMD_RESTORE_OPEN 0x1100` 等）。
- **OB SBT**（`libobk/include/libobk.h:21` + `lib/sbt/libobk.c:207`）：`sbtinit2/sbtbackup/sbtclose2/sbtcommand/sbtend/sbterror/sbtinfo2/sbtread2/sbtremove2/sbtrestore/sbtwrite2`（首参 `struct sbtctx*`，**与达梦 gvar 签名不兼容，不可互换**）；`sbt` shared + `FileTransferAgent` binary（`:12000`）。
- **S3 API**（`s3-tool/s3-service.h:59`）：`InitApi/StopApi/CreateBucket/DeleteBucket/ListBucket/ListObject/UploadObject/DownloadObject/DeleteObject/ObjectExisted/GetObjectSize`；底层链接 eSDKOBS（`s3-tool/xmake.lua:33`）。
- **带宽库**（`bwlimit/lib/bandwidth.h:33`）：`bandwidth_init/bandwidth_config_update/bandwidth_limit_init/bandwidth_reset_limit/bandwidth_limit/bandwidth_exit` + `BW_OP_DOWNLOAD/BW_OP_UPLOAD` + `RPC_SERVER_ID 1 / RPC_CLIENT_ID 2`（`lib/config.h:15`）。
- **FUSE/CLI**：s3mount `mount-file/mount-snapshot`（`fuse.cpp:178`）；afs-cli `main:136`（`--method=list --host --port`）。

---

## 5. 新介质如何接入

```
新增介质（如当年 dmsbtex/libobk）
 → ① 判断接口标准：XBSA 标准 / 数据库 SBT（达梦 DMSBT / Oracle SBT2）/ S3 对象 / 私有协议
 → ② 找最接近的已有模块做范本（§2 表格）：同标准优先仿照（如新 SBT 库仿 dmsbtex 目录结构）
 → ③ 注意签名不兼容陷阱：libobk（ctx 首参）vs dmsbtex（gvar）不可互换，仿照时先对齐目标数据库的头文件
 → ④ 构建接入按 05 §6 三件套（target + version.in + add_deps logger）
 → ⑤ 跨仓检查：介质库的消费方在其他仓库（数据库服务端 dlopen），本仓只保证编译 + 自带 test/simulator 跑通
```

**判据：同标准优先仿照，不同标准优先新建目录**。介质库与备份主链（fs-backup）无编译依赖，各自独立交付（install 分仓见 05）。

---

## 6. 孤岛清单（定位必须过这一关）

| 模块 | 孤岛证据 | 结论 |
|---|---|---|
| `xbsa/` | 除根 xmake/version 外零引用，无任何 `add_deps` | 孤岛：对外交付的 XBSA 库，本仓需求不得引用其实现 |
| `libobk/` | 同上（dmsbtex 命中系 sbt 同名误报，签名已核不兼容） | 孤岛 |
| `dmsbtex/` | 同上；`xmake.lua:26` 甚至注释掉 `-- add_deps("dmsbtex")` | 孤岛 |
| `s3-tool/` | 零链接（仅版本串 + "s3-tools/" 目录名） | 孤岛二进制 |
| `huanweicloun-sdk-s3-data-backup/` | 仅 fs-backup 帮助文本 + third_party OBS.ini，无 `add_deps` | 半孤岛（疑似运行时协作，非编译依赖） |
| `s3tools/libs` vs `huawei/public` | block.h/buffer/obs-service/s3-service 等同名文件两份 | 疑似 fork 未收敛，哪份为主无法确认（缺 README/CODEOWNERS），引用前先实证 |
| OBS.ini 三份重复 | `s3-tool/tests/` + `third_party/huaweicloud-sdk` | 疑似废弃样例，CI 引用关系无法确认 |

> 唯二例外：`bwlimit/` 是现行（被 rpc 三 target `add_deps`，`rpc/xmake.lua:36,64,114`）；s3file 的线程池用的是 `libs` 版（`s3file/main.cpp:497,551`），不是 xbsa 的独立拷贝。

---

## 7. 影响范围

| 组件 | 使用方 | 修改后必须检查 |
|---|---|---|
| `bwlimit/` | rpc 数据面（`rpc-io.cpp:107,183`） | 限速语义变化 rpc 全链路回归 |
| 各介质库接口头 | 外部数据库服务端（dlopen） | 头文件签名变化需外部配合，本仓 test/simulator 先行 |
| `s3tools/libs` vs `huawei/public` 双份 | 各自二进制 | 改一处必须检查另一处是否同改（收敛前） |

---

## 8. 分支差异

- 本分册基于 6.2.0.0（`6200/release`，`fe9d4364`）。他分支的介质矩阵若有差异，差异补记于此，当前为空（待实证）。
