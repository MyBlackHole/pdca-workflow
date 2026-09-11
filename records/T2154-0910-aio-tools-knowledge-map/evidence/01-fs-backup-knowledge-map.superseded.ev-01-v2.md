# fs-backup Knowledge Map（知识地图）

> **文档定位**：本文不是 fs-backup 的目录说明，而是 **「备份能力 → 代码位置 → 任务链」的导航**：收到一个涉及文件备份的需求时，从哪里开始读、核心代码在哪里、如何扩展、何时需要跨模块。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；「使用方」指本仓库内的实际引用位置（均经 grep 实证）；`file:line` 行号易变动，以符号名为准
> **适用分支**：6.2.0.0（目录 `6200/release`），实证 commit `fe9d4364`
> **最后更新**：2026-09-10

---

## 1. 模块组织总览

文件备份子系统 = 用户态三件套（fsclient + fsdeamon + public 静态库）+ 内核模块（fsbackup.ko）+ 调试工具：

| 目录 | 职责 | 关键文件 |
|---|---|---|
| `fs-backup/fsclient/` | fs-cli 客户端：参数解析 + method 分发 + 备份拉取/合并/恢复本地落地 | `fs-backup/fsclient/main.cpp`（handlers 分发表），`fs-backup/fsclient/cli.cpp`，`fs-backup/fsclient/transfer_file.cpp`，`fs-backup/fsclient/restore.cpp`，`fs-backup/fsclient/snapshot.cpp`，`fs-backup/fsclient/config.cpp` |
| `fs-backup/fsdeamon/` | fsdeamon 服务端：TCP 服务 + 多 source 管理 + BackupHelper 进程编排 + 内核同步 | `fs-backup/fsdeamon/main.cpp:297`，`fs-backup/fsdeamon/fs_service.cpp`（`CLIService` 分发），`fs-backup/fsdeamon/fs_source.cpp`，`fs-backup/fsdeamon/backup_helper.cpp`，`fs-backup/fsdeamon/fs_kernel_sync.cpp`，`fs-backup/fsdeamon/unix_server.cpp` |
| `fs-backup/public/` | 公共静态库 `fs_backup_public`：协议帧/元数据状态机/done 解析/工具 | `fs-backup/public/fs_service_proto.h`（命令字），`fs-backup/public/rpc_io.h/.c`（轻量 TCP 帧），`fs-backup/public/fs_meta.h/.cpp`（元数据状态机），`fs-backup/public/fs_done.h`（done 解析），`fs-backup/public/socket_service.h`（服务基类），`fs-backup/public/fsbackup-common.h/.cpp` |
| `fs-backup/kernel/` | 空壳：仅头拷贝，无实现（冗余，见 §7） | `fs-backup/kernel/device/dev_ioctl.h` |
| `fs-backup/tools/` | 手动调试二进制 `fsbackup_tools`：ioctl/meta/done/block 解析 | `fs-backup/tools/main.cpp`，`fs-backup/tools/main_ioctl.cpp`，`fs-backup/tools/main_done.cpp` |
| `fsbackup_kernel_4.x/` | 旧版内核模块源码：hook + 监控 + 字符设备 ioctl | `fsbackup_kernel_4.x/fs_backup.c`（模块入口），`fsbackup_kernel_4.x/device/fsbackup_driver.c`（ioctl 分发），`fsbackup_kernel_4.x/sys/sys_hook.c`，`fsbackup_kernel_4.x/conf/hook_conf.h` |
| `fs-backup/doc/` + `fs-backup/README.md` | 契约文档：端口/流程/FAQ 唯一可信源 | `fs-backup/doc/readme.md` |

> **一句话记忆**：fsclient 是「发命令 + 拉数据 + 本地落地」，fsdeamon 是「管 source + 调内核 + 回数据」，public 是「两者的公共语言（帧/元数据/命令字）」，内核模块是「眼睛（监控文件变化）」。

---

## 2. 能力总览（能力 → 代码 → 使用方）

| 能力 | 解决什么问题 | 核心代码位置 | 主要入口 | 使用方 |
|---|---|---|---|---|
| **增量元数据状态机** | 跟踪 open/create/write/trunc/delete，生成 meta + bitmap | `fs-backup/public/fs_meta.h:52`（`FsMeta`）+ `fs_meta.cpp`（`InitFsMeta/OnWriteFile/OnBegin`） | `FsMeta::OnWriteFile/OnCreatePath/OnDeletePath/UpdateBitmap` | fsdeamon（`backup_helper.h:168` 成员 `m_fs_meta`）；fsclient（`transfer_file.cpp`、`restore.cpp`、`snapshot.cpp`、`cli.cpp`） |
| **done 日志解析** | 解析内核落盘日志推进快照 | `fs-backup/public/fs_done.h:13`（`DoneParse`） | `DoneParse` 方法族（具体签名以代码为准） | fsdeamon（`backup_helper.h:169`）；`tools/main_done.cpp` |
| **轻量 TCP 帧** | fs-cli ↔ fsdeamon 自定义 header+body 收发 | `fs-backup/public/rpc_io.h:17-21` + `rpc_io.c:73,138` | `rpc_send/rpc_recv/rpc_recv_header/rpc_recv_body` | fsclient 全文件；fsdeamon（`fs_service.cpp:157,243` `CLIService`） |
| **建连/文件拷贝** | 统一 connect + mkdir_path + file_copy | `fs-backup/public/fsbackup-common.h:32` + `fsbackup-common.cpp:210` | `open_service/file_copy/write_file_txt` | `fsclient/main.cpp:590`；`fsdeamon/fs_source.cpp:520,840`；`fsclient/cli.cpp:617` |
| **Socket 服务基类** | 监听 + 每连接线程分发 | `fs-backup/public/socket_service.h/.cpp:11` | `SocketService::StartServiceThread/OnAccept` | `fsdeamon/fs_service.h:20`（`FsService : public SocketService`）；`fsdeamon/main.cpp:409` |
| **内核 ioctl 封装** | 经 aio-speedd 转发到内核设备 | `fs-backup/fsdeamon/fs_kernel_sync.h:15-42` + `fs_kernel_sync.cpp` | `FsKernel_AddTrackup/DelTrackup/AddExclude/SyncStatOne/LogSwitch` | `fsdeamon/fs_source.cpp:713`；`backup_helper.cpp:504-512`（`WithSession` 回调内） |
| **远程拉取备份数据** | 按 meta 枚举 + 多线程落本地 `data/` | `fs-backup/fsclient/transfer_file.h:8` + `transfer_file.cpp:709` | `TransferTargetPath` | 唯一使用方 `fsclient/cli.cpp:752`（`make_backup` 尾部） |
| **本地恢复** | 按 meta+data 在全量上重放增删改 | `fs-backup/fsclient/restore.h:6` + `restore.cpp:514` | `RestoreBackup` | 唯一使用方 `fsclient/cli.cpp:239`（`restore_backup`） |
| **本地合并快照** | 反序 merge 多个 `FS_META` 到 `_merge/meta` | `fs-backup/fsclient/snapshot.h:4` + `snapshot.cpp:9` | `do_merge_snapshot` | `fsclient/cli.cpp:990`（经 `do_merge_snapshots:954`） |

---

## 3. 核心任务链

### 3.1 快照

```
fsclient/main.cpp:508,566 handlers[snapshot → FS_BACKUP]
  → fsclient/cli.cpp:140 make_snapshot : rpc_send(FS_BACKUP)
  → fsdeamon/fs_service.cpp:191-192 CLIService → pFsSource->Snapshot
  → fsdeamon/fs_source.cpp:562,611 FsSource::Snapshot → client->DoSnapshot
  → fsdeamon/backup_helper_client.cpp:100 BackupHelperClient::DoSnapshot
  → fsdeamon/backup_helper.cpp:444,504-512 BackupHelper::DoSnapshot
    → FsKernel_SyncStatOne + FsKernel_LogSwitch（内核同步 + 日志切换）
```

### 3.2 备份

```
fsclient/main.cpp:510 backup → FS_CHECK → make_backup:551
  → fsclient/cli.cpp:625,642 rpc_send(FS_CHECK) + rpc_recv
  → fsdeamon/fs_service.cpp:209 → CheckSource
  → fsdeamon/fs_source.cpp:827 CheckSource（回 snap_path/source_host/port/exclude-dir）
  → fsclient/cli.cpp:727,752 do_scp_download(meta) + TransferTargetPath（经 rpc 拉数据）
```

### 3.3 恢复（纯本地，daemon 不参与）

```
fsclient/main.cpp:511,583 restore → FS_RESTORE（跳过 open_service）
  → fsclient/cli.cpp:206 restore_backup（拼 _inc/_merge/ 路径）
  → fsclient/restore.cpp:514 RestoreBackup
```

> 实证：`fsdeamon/fs_service.cpp:187-233` switch 无 `FS_RESTORE` 分支，服务端不参与恢复是设计如此，非缺失。

### 3.4 删除备份

```
fsclient/main.cpp:512 del-backup → FS_DEL_BACKUP → del_backup:248
  → fsdeamon/fs_service.cpp:193-195 → DelSnapshot
  → fsdeamon/fs_source.cpp:623 DelSnapshot
  → 成功后 fsclient/cli.cpp:304 本地 dir_clear
```

### 3.5 监控增删（直达内核）

```
fsclient/main.cpp:513-514 add/del-trackup → trackup:313
  → fsdeamon/fs_service.cpp:197-201 → AddTrackup/DelTrackup
  → fsdeamon/fs_source.cpp:797,809
  → fsdeamon/fs_kernel_sync.cpp:45 FsKernel_AddTrackup → do_fsbacup_dev_ioctl
  → rpc/rpc.cpp:1410,1537 → rpc/rpc-server.cpp:2688（aio-speedd 转发）
  → fsbackup_kernel_4.x/device/fsbackup_driver.c:141,156 SET/DEL_BACKUP_PATH
```

### 3.6 内核监控链

```
fsbackup_kernel_4.x/fs_backup.c:22,54 init_fsbackup_module
  → sys_hook_init + fsbackup_dev_init
  → fsbackup_kernel_4.x/sys/sys_hook.c:29（hook）
  → fsbackup_kernel_4.x/device/fsbackup_driver.c:81（ioctl 分发）
  → fsbackup_kernel_4.x/conf/hook_conf.h:44-56（配置/日志切换）
```

> 挂载：全仓 `mount|挂载` 在 fs-backup/ 零命中，`doc/readme.md` 无挂载流程——**本子系统无挂载能力**，勿臆测。

---

## 4. 协议契约（跨模块隐式契约，逐字核对）

### 4.1 method 字符串（cli → daemon）

`fs-backup/fsclient/main.cpp:506-529`：`list/snapshot/merge-snapshot/backup/restore/del-backup/add-trackup/del-trackup/add-exclude/del-exclude/add-source/del-source/update-source-host/list-source/check/debug-source/update-log-dir/fsdev-read-count/fsdev-decr-count/reload-config/show-config`。文档子集见 `fs-backup/doc/readme.md:39,52-76`。

### 4.2 FS_ 命令字

`fs-backup/public/fs_service_proto.h:19-40`：`FS_LIST=1, FS_BACKUP=2, FS_RESTORE=3, FS_DEL_BACKUP=4, FS_BITMAP=5, FS_ADD_TRACKUP=6, FS_DEL_TRACKUP=7, FS_ADD_EXCLUDE=8, FS_DEL_EXCLUDE=9, FS_ADD_SOURCE=10, FS_DEL_SOURCE=11, FS_UPDATE_SOURCE_HOST=12, FS_LIST_SOURCE=13, FS_CHECK=14, … FS_SNAPSHOT_LIST=19, FS_RELOAD_CONFIG=20, FS_SHOW_CONFIG=21, FS_FIND_SOURCE=22`。

> 注意复用：`backup → FS_CHECK`、`merge-snapshot → FS_SNAPSHOT_LIST`（`main.cpp:509-510`），不是一对一。

### 4.3 ioctl 字（三份拷贝须一致）

`fs-backup/kernel/device/dev_ioctl.h:4-15` = `fsbackup_kernel_4.x/device/dev_ioctl.h` = `rpc/dev_ioctl.h`：`100000 READ_COUNT，100001 INCR_COUNT，100002 READ_PIDS，100003 SET_BACKUP_PATH，100004 DEL_BACKUP_PATH，100005 SET_EXCLUDE，100006 DEL_EXCLUDE，100007 META_SYNC，100008 LOG_SWITCH，100009 UPDATE_LOG_DIR`。工具侧 `tools/main_ioctl.cpp:47-59`；转发侧 `rpc/rpc.cpp:1433-1509` + `rpc/rpc-server.cpp:2618-2691`。

### 4.4 端口与路径约定

| 契约 | 值 | 出处 |
|---|---|---|
| fsdeamon 默认端口 | `8901` | `fsdeamon/config.cpp:116`，`main.cpp:59` |
| 本地/远端 aio-speedd 默认端口 | `6611` | `fsclient/config.cpp:94-95`；`--rpc-port` 必须指本地 6611（`doc/readme.md:138` FAQ） |
| 拓扑 | 源端 8811 / 备份侧 8901+6611 | `doc/readme.md:110-129` |
| 内核配置/数据 | `/etc/fsbackup/main.conf[.tmp]` + `/var/fsbackup/` | `hook_conf.h:11-14`，`doc/readme.md:7-9` |
| daemon 数据 | `<data>/.main` + `<data>/<source>/.main` | `fs_service.cpp:45`，`fs_source.cpp:47` |
| unix sock | `fsdeamon.sock` / `network.sock` / `worker.sock` / `backup.sock` | `unix_server.h:8`，`main.cpp:279-281,358,391`，`backup_helper.h:28` |
| 备份落盘 | `<path>/<name>_{full,inc,merge}/data\|meta\|path\|FS_META` | `cli.cpp:587-602` |

---

## 5. 新能力如何复用或扩展

```
新需求需要某个备份能力
 → ① 搜 §2 总表：这个能力是不是已经存在？
 → ② 存在 → 直接复用对应类/函数；看 §6 影响范围确认改动面
 → ③ 不存在但相近 → 扩展已有组件：
        · 新客户端命令 → main.cpp handlers 加 method + cli.cpp 加实现 + daemon CLIService 加分支
        · 新内核监控项 → driver 加 ioctl 字（三份 dev_ioctl.h 同步）+ fs_kernel_sync 加封装
        · 新元数据类型 → FsMeta 加 OnXxx 方法 + DoneParse 加解析
 → ④ 全新能力域 → 新增文件放对目录（客户端逻辑→fsclient/，服务端逻辑→fsdeamon/，两者共享→public/）
```

**什么情况下不应该放入 fs-backup**：

- **传输通道逻辑**：远端执行/文件块传输属于 `rpc/`，fs-backup 只调用 `rpc_session_start/do_scp_download` 等接口（见 02）。
- **通用基础能力**：日志/线程/配置/位图属于 `libs/`（见 03）。
- **新存储介质**：S3/XBSA/SBT 介质属于 04 的领域，勿在 fs-backup 内另起炉灶。

---

## 6. 影响范围

| 组件 | 使用方 | 修改后必须检查 |
|---|---|---|
| `public/fs_service_proto.h`（命令字） | fsclient + fsdeamon 全链路 | 两侧 switch 分支同步；拼错即无响应 |
| `public/fs_meta.h`（元数据状态机） | fsdeamon 备份 + fsclient 恢复/合并 | 备份/恢复/合并三链路回归 |
| `public/rpc_io.h`（帧） | cli ↔ daemon 全部通信 | 全 method 回归 |
| `fsdeamon/fs_service.cpp`（分发） | 全部 method | 新增 method 必须加分支 |
| 内核 driver（ioctl） | fs_kernel_sync 经 rpc 转发 | 三份 dev_ioctl.h 一致性 + 内核模块重装 |

---

## 7. 孤岛与冗余

- `fs-backup/kernel/`：仅 1 头文件，与另两份 `dev_ioctl.h` 无差异，零独立实现——冗余拷贝，认准内容即可，勿当新接口。
- `FS_BITMAP=5`：`handlers[]` 无 bitmap 项（仅 `cli_help.cpp:94` 示例残留），`CLIService:187-233` 无分支——疑似废弃，先实证再引用。
- `public/channel.h/c`、`thread_control.*`、`safe_queue.h/safe_map.h`：全仓零外部引用——孤岛，勿引用。
- `tools/`、`public/tests/*`、`fsdeamon/tests/`：生产代码零引用，调试/测试专用。
- `*.o/*.ko/.tmp_versions/` 入库：构建污染，非源码，勿读勿改。

---

## 8. 分支差异

- 本分册基于 6.2.0.0（`6200/release`，`fe9d4364`）。他分支（6100/6110 等）的 fs-backup 结构若有差异，差异补记于此，当前为空（待实证）。
