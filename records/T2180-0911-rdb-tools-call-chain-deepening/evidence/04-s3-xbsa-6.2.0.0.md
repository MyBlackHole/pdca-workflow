# S3 与介质扩展 Knowledge Map（知识地图）

> **文档定位**：本文是对象存储与第三方介质子系统的导航—— **「介质能力 → 代码位置 → 对外契约」**，以及全仓最重要的 **孤岛清单**：哪些模块仓内零引用、引用即错。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；`file:line` 行号易变动，以符号名为准
> **依据**：aio-tools 6200/release 实际代码 + 仓内引用统计（基线：目录 6200/release，commit fe9d4364）
> **版本化**：本文为 6.2.0.0 版代码地图，地图与代码基线强绑定；读前先按 00-index §〇 版本路由选版本，再读对应目录下的 `<tag>.md`
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

## 9. s3-tool 逐操作调用链

状态：`external/operator`；仓内无业务调用者。公共前缀与收尾：`s3-tool/main.cpp:main -> args_process -> Arguments::Verify -> S3Service::InitApi`，按 `s3/upload/download/LIST` 分发，最后 `close_logger -> S3Service::StopApi`。

```text
upload（本地 -> S3）
s3-tool/main.cpp:main -> UploadFileToS3
  -> [目录] s3-tool/common.cpp:dir_traversal_2
     -> create_thread(UploadObjectToS3Thread) -> S3Service::UploadObject
  -> [单文件] S3Service::UploadObject
  -> s3-tool/obs-service.cpp:ObsService::UploadObsObject
  -> 华为 eSDK OBS put_object/multipart 回调
返回：ScpManage running/error -> stdout + main 返回码
```

| 操作分支 | 核心调用链 | 结果 |
|---|---|---|
| `--download` | `main -> DownloadFileFromS3 -> S3Service::ListObject -> create_thread(DownloadObjectFromS3Thread) -> S3Service::DownloadObject -> ObsService::DownloadObsObject` | 写 `--dst-path`，聚合线程错误 |
| `--list` | `main -> ListFileFromS3 -> S3Service::ListObject -> ObsService::ListObsObject` | JSON objects/next_marker 到 stdout |
| `--s3` | `main -> DownloadFromS3ToS3 -> ListObject -> create_thread(CopyObjectFromS3ToS3Thread) -> 源 S3Service::DownloadObject(cache) -> 目标 S3Service::UploadObject` | cache 清理 + 迁移结果 |

## 10. s3file 逐操作调用链

状态：`external/operator`。入口 `s3tools/s3file/main.cpp:main -> s3file_init_config -> argp_parse`，位置参数在 `parse_opt` 映射：`get/up/rm/upload-snapshot/check-snapshot/destroy-snapshot`。

| subcommand | 分发符号 | 核心链与结果 |
|---|---|---|
| `get` | `s3_to_local` | `S3Service::ListObject -> thread_task_post(download_thread) -> S3Service::DownloadObject`，写本地路径 |
| `up` | `local_to_s3` | `TestIsDir -> dir_traversal_2 -> thread_task_post(upload_thread) -> S3Service::UploadObject` |
| `rm` | `rm_s3` | `ListObject(分页) -> thread_task_post(rm_thread) -> S3Service::DeleteObject` |
| `upload-snapshot` | `upload_snapshot_to_s3` | 解析 stdin ZFS stream、分 bundle、上传对象和快照元数据 |
| `check-snapshot` | `check_destroy_snapshot` | `S3HandlerHelper::EnsureSnapshotAndRead/ReadSnapshotObjectList/ReadZfsSnapshotBitmap* -> ObjectExisted`，验证可销毁性 |
| `destroy-snapshot` | `destroy_snapshot` | 读快照关系/bitmap/object list，重写邻接元数据并删除不再引用对象 |

`upload-snapshot` 代表链：

```text
s3tools/s3file/main.cpp:main（CMD_UPLOAD_SNAPSHOT）
  -> upload_snapshot_to_s3
  -> s3tools/libs/zfs-tools.c:zfs_stream_begin
  -> zfs_stream_bundle_block_proc（解析 DRR_* 与块范围）
  -> libs/thread_pool.c:thread_task_post(upload_snapshot_bundle_to_s3)
  -> upload_snapshot_bundle_to_s3
  -> S3Service::PutObject
  -> ObsService/eSDK OBS put_object
  -> S3HandlerHelper::SaveZfsSnapshot/SaveZfsSnapshotBitmap/SaveSnapshotObjectList
返回：等待线程池；写 cache 中 bcm/对象索引；main 返回 error
```

## 11. s3mount FUSE 调用链

状态：`external/FUSE`。`mount-file` 与 `mount-snapshot` 在 `parse_opt` 分开，并在 `init_operations` 装配不同 callback 表。

```text
s3tools/s3mount/fuse.cpp:main
  -> s3mount_init_config -> argp_parse
  -> ObsService::InitSDK -> new S3Service
  -> [CMD_MOUNT_FILE] init_s3_filesystem（ListObject 建 node tree）
     [CMD_MOUNT_SNAPSHOT] FuseFileSystemMap::Init（读快照/bitmap 元数据）
  -> s3tools/s3mount/fuse-operations.cpp:init_operations(cmd)
  -> libfuse:fuse_main
  -> kernel VFS callback -> fs_*（snapshot）或 file_*（object file）
返回：callback errno/bytes -> FUSE -> 调用进程；退出后 ShutdownSDK
```

`mount-snapshot` callback 共 30 个：`getattr/readlink/mknod/mkdir/unlink/rmdir/link/symlink/rename/chmod/chown/utimens/truncate/open/read/write/statfs/flush/fsync/release/opendir/readdir/init/destroy/access/create/setxattr/getxattr/listxattr/removexattr`。主数据链为 `fs_open -> FuseFileSystemMap::OpenFuseFile`，`fs_read/fs_write -> ReadFuseFile/WriteFuseFile`，`fs_release -> CloseFuseFile`；这些方法再通过 `S3Service` 与 cache/快照对象交互。

`mount-file` 装配同名 `file_*` 集合，但 `readlink/mknod/mkdir/unlink/rmdir/link/symlink/rename/truncate/write/setxattr/getxattr/listxattr/removexattr` 固定返回 `-EROFS`；有效读链：`file_open -> find_node -> [未下载] g_pS3Service->download_file -> open(cache)`，随后 `file_read -> pread`，`file_release -> close`。`flush/fsync` 未装配，状态 `isolated implementation`。

## 12. afsd FUSE 调用链

状态：`external/FUSE service`。它不是 8892 TCP 服务：6.2.0.0 的 `my-fuse/fuse.cpp` 没有 `socket/bind/listen/accept`，只进入 FUSE；因此 afs-cli 的网络 method 不能闭合到此 target。

```text
huanweicloun-sdk-s3-data-backup/my-fuse/fuse.cpp:main
  -> args_process -> ObsService::InitSDK -> new S3Service
  -> FuseFileSystemMap::Init + LocalFileSystemMap::Init/Open
  -> huanweicloun-sdk-s3-data-backup/my-fuse/fuse-operations.cpp:init_operations
  -> libfuse:fuse_main
  -> fs_open
     -> snapshot：FuseFileSystemMap::OpenFuseFile
     -> local：LocalFileSystemMap::OpenFile
  -> fs_read/fs_write
     -> snapshot：ReadFuseFile/WriteFuseFile（S3/cache）
     -> local：pread/pwrite
  -> fs_release -> CloseFuseFile/CloseFile
返回：bytes/errno -> FUSE；退出时 ShutdownSDK 并释放 maps
```

已装配的 30 个 callback 与 §11 `mount-snapshot` 同名；`fs_readlink/link/truncate/statfs/xattr` 等若函数体固定返回成功/空结果，源码现状即如此，不应推断其具备完整 POSIX 语义。

## 13. afs-cli 逐 method 调用链

状态：`external client`。入口 `huanweicloun-sdk-s3-data-backup/my-fuse/afs-cli.cpp:main -> args_process -> g_request_handlers`，18 个 method 全量如下。

### 13.1 无网络、直接 SDK/本地计算的 12 个 method

| method | 调用链 | 结果 |
|---|---|---|
| `create-bucket` | `sdk_create_bucket -> S3Service::CreateBucket -> ObsService::CreateObsBucket` | S3 status |
| `delete-bucket` | `sdk_delete_bucket -> [admin==afs-root] recursion -> S3Service::DeleteBucket` | S3 status |
| `upload-object` | `upload_object -> do_upload_object -> [gmssl] sm4_cbc_encrypt_* -> S3Service::UploadObject` | 对象/临时密文 |
| `download-object` | `download_object -> ObjectExisted -> DownloadObject -> [meta gmssl] sm4_cbc_decrypt_* -> write` | `--output` 文件 |
| `delete-object` | `sdk_delete_object -> ObjectExisted -> DeleteObject` | S3 status |
| `upload-meta` | `upload_meta -> do_upload_object(base=s_logMateData)` | 元数据对象 |
| `download-meta` | `download_meta -> download_object` | 元数据文件 |
| `delete-meta` | `delete_meta -> sdk_delete_object` | 删除结果 |
| `destroy-snapshot` | `destroy_snapshot_check_option -> destroy_snapshot -> S3HandlerHelper/bitmap -> DeleteObject tasks` | 更新快照链并删除对象 |
| `check-destroy-snapshot` | `check_destroy_snapshot -> ReadZfsSnapshot/ReadSnapshotObjectList/ReadZfsSnapshotBitmap* -> ObjectExisted` | 检查结果 |
| `destroy-zvol` | `destroy_zvol -> S3HandlerHelper::ReadZfsSnapshot -> 删除 zvol 元数据/对象` | S3 status |
| `version-detect` | `version_detect_check_option -> version_detect -> S3HandlerHelper::EnsureSnapshotAndRead` | 版本/快照状态 |

### 13.2 长度前缀 JSON 网络 method（未闭合）

```text
list-file/lock-snapshot/unlock-snapshot/full-cache/snapshot-cache-stat/local-cache-stat
huanweicloun-sdk-s3-data-backup/my-fuse/afs-cli.cpp:main
  -> huanweicloun-sdk-s3-data-backup/my-fuse/cli.cpp:open_afsd（TCP，默认 8892）
  -> 对应 method 函数构造 JSON {method: ...}
  -> write(htonl(length)) -> write(JSON)
  -> read(length/JSON) 或 read(JSON) -> verify_response/stdout
  -> 对端：6.2.0.0 仓内未找到 TCP listen 或 method 消费 switch
```

结论：发送端 method 字符串已实证，但 `afsd` target 仅 FUSE，接收端未闭合；不能写成“afs-cli -> afsd handler”。需要部署包/其它仓库或历史版本证据才能继续。

## 14. xbsa64 导出 ABI 调用链

状态：`external shared ABI`；真实备份软件调用者在仓外。头文件 `xbsa/src/xbsa/xbsa.h` 共 16 个导出操作。

### 14.1 会话、写入与事务

```text
外部 XBSA consumer
  -> xbsa/src/xbsa/xbsa.c:BSAInit
  -> xbsa_env_handler/xbsa_new_config（解析 XBSA config/storagepath）
  -> BSABeginTxn（当前仅返回 SUCCESS）
  -> BSACreateObject
     -> tb_path_absolute_to
     -> FILE：tb_file_init(append/overwrite/trunc)；DIRECTORY：tb_directory_create
     -> tb_file_info -> 回写 copyId
  -> BSASendData -> tb_file_writv（可按 rch 后缀跳 10 字节）
  -> BSAEndData -> tb_file_sync
  -> BSAEndTxn -> tb_file_exit/tb_list_exit（vote 分支当前无额外动作）
  -> BSATerminate -> xbsa_free_env/xbsa_free_config/tb_free
返回：每步 BSA_RC_* 给外部 consumer
```

### 14.2 查询与读取

```text
BSAQueryObject
  -> tb_path_absolute_to -> glob_recursive
  -> tb_file_info -> 构造 BSA_ObjectDescriptor list
  -> 返回首项并推进 iterator
BSAGetNextQueryObject
  -> iterator next -> tb_path_relative_to -> 回写 descriptor
  -> 尾部返回 BSA_RC_NO_MORE_DATA
BSAGetObject
  -> tb_path_absolute_to -> tb_file_init(TB_FILE_MODE_RO)
BSAGetData
  -> tb_file_read -> BSA_DataBlock32.numBytes
返回：descriptor/data block/BSA_RC_*
```

其余 ABI：`BSADeleteObject` 当前只校验 handle 后返回成功；`BSAGetLastError` 与 `BSAGetEnvironment` 当前只返回成功；`BSAQueryApiVersion` 回 `1.1.1`；`BSAQueryServiceProvider` 计算 `"aio xbsa"` 长度，但对 `providerPtr` 仅重定向局部指针。它们是 `external` ABI 中的 `stub/incomplete` 分支，不能描述为完整删除/错误/环境实现。

## 15. rch-tools 逐类型调用链

状态：`external/operator`。公开分支只有 `--data-type=data|xlog`，输入清单来自 `--file-list` 或目录遍历。

```text
xbsa/src/main.c:main -> args_process
  -> [无 file-list] xbsa/src/utils/dir.c:traverse_directory -> directory_walk_func
     [有 file-list] fgets -> session.head
  -> xbsa/src/utils/thread_pool.c:thread_pool_init
  -> switch DATA_TYPE_DATA
     -> data_process -> rch_check_file_name
     -> thread_task_post(do_data_process)
     -> rch_set_conf -> xbsa/src/rch/rch.c:rch_parse
  -> switch DATA_TYPE_XLOG
     -> xlog_process -> xlog_check_file_name
     -> thread_task_post(do_xlog_process)
     -> xbsa/src/xlog/xlog.c:xlog_parse
  -> thread_pool_destroy -> 汇总每 path status/file-err
返回：解析文件写到 output-path，错误项写 file-err
```

## 16. sbt ↔ FileTransferAgent 调用链

状态：`external shared ABI + external service`；自带 test/simulator 是示例消费者，不是产品数据库联调。

### 16.1 SBT2 公开操作

`libobk/lib/sbt/libobk.c:sbtinit` 把 11 个函数装入 `global.api`：`sbtinit2/sbtbackup/sbtclose2/sbtcommand/sbtend/sbterror/sbtinfo2/sbtread2/sbtremove2/sbtrestore/sbtwrite2`。

```text
外部 OceanBase/RMAN consumer -> sbtinit -> SBTOPT_API 函数表
  -> sbtinit2
  -> getAIOServHost/getAIOServPort/getAIOServBackupDir
  -> socket/connect(FileTransferAgent:12000)
  -> sbtbackup
  -> sendOpenBackupSliceRequest(active_open_backup_slice,bk_write)
  -> FileTransferAgent:_network -> bkFunctions[0] -> openBackupSlice
  -> recvOpenBackupSliceResponse
  -> sbtwrite2 -> sendPostBackupSlice(active_post_bkdata_slice)
  -> bkFunctions[2] -> postBackupSlice -> write/compress/checksum
  -> sbtclose2 -> sendCloseBackupFileRequest -> closeBackupFile
  -> sbtend -> sendCloseBackupSliceRequest -> closeBackupSlice -> close socket/log
返回：每次 activeioHeader response -> SBT 返回码
```

恢复链：`sbtrestore -> [localpath_enabled] open(local)`；否则 `sendOpenBackupSliceRequest(bk_read) -> openBackupSlice`，随后 `sbtread2 -> recvPostBackupSlice` 接收 `postBackupSlice` 数据，`sbtclose2/sbtend` 收尾。信息/删除链：`sbtinfo2 -> sendStatBackupSliceRequest -> statBackupSlice -> recvStatBackupSliceResponse`；`sbtremove2 -> sendRemoveBackupSliceRequest -> removeBackupSlice -> recvRemoveBackupSliceResponse`。`sbtcommand` 当前固定成功，`sbterror` 只回 `ctx->error/strerror`。

### 16.2 FileTransferAgent 对端分发

```text
libobk/main.c:main -> socket/bind/listen(:12000)
  -> select -> accept -> libobk/lib/logic/oracleCmdTbl.c:startWorker
  -> _network -> _baseRecv(activeioHeader)
  -> bkFunctions[cmdId]
     0 openBackupSlice
     1 closeBackupSlice
     2 postBackupSlice
     3 statBackupSlice
     4 removeBackupSlice
     5 closeBackupFile
  -> 对应 response activeioHeader(dType=1)
返回：socket；线程完成经 eventfd 通知 main
```

## 17. dmsbtex ↔ dm-ftp 调用链

状态：`external shared ABI + external service`；签名使用 `void *gvar`，与 §16 `struct sbtctx *` 不兼容。

### 17.1 DMSBT 13 个 ABI

`dmsbtex/sbt.c` 导出：`sbtversion/sbtinit/sbtinit2/sbtbackup/sbtwrite/sbtclose/sbtinfo/sbtend/sbtrestore/sbtread/sbterror/sbtcommand/sbtdelete`。

```text
外部达梦 consumer
  -> dmsbtex/sbt.c:sbtinit（分配 dmsbtex_t/gvar，返回能力参数）
  -> sbtinit2（解析 SBTINIT2_* -> init_sbt_config）
  -> socket/connect(dm-ftp)
  -> sbtbackup
  -> dmsbtex/network.c:send_packet(CMD_BACKUP_OPEN)
  -> dmsbtex/main.c:_worker -> switch CMD_BACKUP_OPEN -> OnBackupOpen -> open
  -> send_packet(CMD_BACKUP_OPEN_RESP) -> recv_packet
  -> sbtwrite -> 分块 send_packet(CMD_BACKUP)
  -> _worker -> OnBackup -> write
  -> sbtclose（CMD_BACKUP_CLOSE） -> OnBackupClose -> close -> *_RESP
  -> sbtend -> close agent/free/logger
返回：DMSBT SBT_EC_SUCCESS/SBT_EC_FAIL
```

恢复链：`sbtrestore -> send_packet(CMD_RESTORE_OPEN) -> OnRestoreOpen -> open -> *_RESP`，`sbtread -> CMD_RESTORE(read_bytes) -> OnRestore -> read -> CMD_RESTORE_RESP + data`，`sbtclose -> CMD_RESTORE_CLOSE -> OnRestoreClose`。`sbtversion` 与 `sbtinfo` 只读本地结构；`sbterror/sbtcommand/sbtdelete` 当前只校验配置并返回成功，没有网络操作，状态 `stub/incomplete`。

### 17.2 dm-ftp 对端分发

```text
dmsbtex/main.c:main -> start_server(0.0.0.0, g_listen_port)
  -> select -> accept -> startWorker
  -> _worker -> dmsbtex/network.c:recv_packet
  -> switch network_header_t.cmd
     CMD_BACKUP_OPEN -> OnBackupOpen
     CMD_BACKUP -> OnBackup
     CMD_BACKUP_CLOSE -> OnBackupClose
     CMD_RESTORE_OPEN -> OnRestoreOpen
     CMD_RESTORE -> OnRestore
     CMD_RESTORE_CLOSE -> OnRestoreClose
  -> send_packet(CMD_*_RESP)
返回：备份侧落文件，恢复侧回数据/errno；线程结束经 eventfd 回收
```
