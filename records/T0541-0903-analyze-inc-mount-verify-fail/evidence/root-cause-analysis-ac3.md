# 增量备份 mount_verify 临时目录导致 EEXIST 失败根因分析（T0541）

> 状态：纯分析，不修改代码。所有结论带 `file:line` 或可复跑命令。

## 1. 现象（可复核）

日志（2026-09-02 18:06:06）：

```
fs-backup/fsclient/transfer_file.cpp:485 fs_path_callback| /DISK_CHECK* is del, ignore it
...
fs-backup/fsclient/transfer_file.cpp:445 backup_new_directory: /mount_verify_20260902 (remote: /var/lib/greatdb-cluster/datanode1/mount_verify_20260902)
rpc/rpc.cpp:1988 rpc_conn_cli_readdir_tree| recv response failure. File exists(errno: 17)
fs-backup/fsclient/transfer_file.cpp:456 backup_new_directory: readdir_tree ... failed, ret=-3
fs-backup/fsclient/transfer_file.cpp:491 fs_path_callback| backup_new_directory /mount_verify_20260902 failed
PathForEachCallback failed
fs-backup/fsclient/cli.cpp:755 make_backup| transfer target path failed.
```

随后 `rpc/rpc-command.cpp:236 do_scp_download` 对 `binlog.000029/000030/...` 仍显示 `status completed success`，说明线程池中已投递任务继续完成，但 `TransferTargetPath` 整体仍以失败收场。

## 2. 证据链（按调用栈自底向上）

1. **入口** `fs-backup/fsclient/cli.cpp:753` `make_backup` → `fs-backup/fsclient/transfer_file.cpp:709` `TransferTargetPath` → `transfer_file.cpp:778` `TransferIncrementData`（`full_bak=false`）。
2. **遍历** `transfer_file.cpp:551` `TransferIncrementData` 初始化 `FsMeta` 后 `transfer_file.cpp:651` `meta.PathForEachCallback(fs_path_callback)`。`fs-backup/public/fs_meta.cpp:779` 顺序遍历 `FSMETA_DB_PATH`，对本次 `path=/mount_verify_20260902, type=TYPE_NEW, st_mode=S_ISDIR` 进入 `transfer_file.cpp:488-494` 分支，置 `covered_prefix=path` 后 `backup_new_directory(ctx, path, path_tmp)`。
3. **建本地目录** `transfer_file.cpp:448` `mkdir_path(local)` 对 `data_save_path + "/mount_verify_20260902"` 成功（`libs/common.c:71` 在 `EEXIST` 时返回 0，但保留 `errno=17` 未清零，见 §4）。
4. **拉远端目录树** `transfer_file.cpp:453` `rpc_conn_cli_readdir_tree(ctx->dir_rpc_conn, remote_root)`（`rpc/rpc.cpp:1958`）。`rpc/rpc-server.cpp:3069` `rpc_conn_srv_readdir_tree` 先回 `rc=0,errno=0` 的 ACK，随后 `libs/dir_utils.c:281` `dir_traversal_at(AT_FDCWD, remote_dir)` 在远端该路径已消失/卸载时 `openat(O_DIRECTORY)` 失败 `ENOENT/ENOTDIR` 返回 -1，`rpc-server.cpp:3133` 记录 `traversal_error=-1`，并发 `0` 结束包后 `rpc-server.cpp:520-530` 因 `ret!=0` 跳出服务循环并 `rpc_conn_free` 关闭连接。
5. **客户端感知失败** `rpc/rpc.cpp:1986` `rpc_conn_is_ready_recv_msg` 对首包或后续 chunk 的 `rpc_recv_msg` 收到 `IO_EOF=0xfffffffd=-3`（`rpc/rpc-io.h:18`），`rpc.cpp:1988` 打印 `recv response failure. File exists(errno:17)`（stale，见 §4），上层得 `ret=-3`，`transfer_file.cpp:456` 判错后 `transfer_file.cpp:491` → `fs_path_callback` 返回 -1 → `fs_meta.cpp:833` 使 `PathForEachCallback` 返回 -1 → `transfer_file.cpp:654` 打印失败并经 `TransferIncrementData:exit` 与 `cli.cpp:780` 向上传播。

## 3. 根因分级

| 级别 | 结论 | 依据 |
|------|------|------|
| **直接诱因** | 远端 `/mount_verify_20260902` 为 GreatDB 集群临时挂载校验目录，在 `FsMeta` 快照与 `readdir_tree` 之间已被删除/卸载，导致服务端 `dir_traversal_at` 失败并关闭连接，客户端得 `IO_EOF(-3)` | `transfer_file.cpp:445` 路径与 `DISK_CHECK* is del` 旁路表明同批存在大量短命路径；`dir_traversal_at:openat` 对不存在目录返回 -1 的行为确定 |
| **链路因** | 增量路径对“新建目录在拉取时消失”未做容错，`backup_new_directory` 与 `fs_path_callback` 将任意失败视为致命，中断整批备份 | `transfer_file.cpp:455-458,490-493` 无区分；全量路径 `TransferTargetPath:full_bak=true` 走 `rpc_download_file` 不经此链路故不受影响 |
| **污染因（噪音）** | 日志中 `File exists(errno:17)` 并非本次真因，系 `mkdir_path:78-80` 成功但残留 `errno=EEXIST` 的 stale 值被 `rpc.cpp:1988` 原样打印；真因是 `ret=-3(IO_EOF)` | `common.c:78` `mkdirat==0 || errno==EEXIST → return 0` 未清 `errno`；`-3` 与 `IO_EOF` 值吻合（`rpc-io.h:18`） |

**排除**：`File exists` 非服务端 `mkdir` 冲突；`DISK_CHECK*` 已因 `TYPE_DEL` 在 `transfer_file.cpp:484-485` 被正确跳过，非本次中断点。

## 4. 影响面

- **受影响**：仅增量（`TransferIncrementData`）且命中 `TYPE_NEW|S_ISDIR` 的短命临时目录时；`mount_verify_20260902` 这类空或已消失目录会必现中断。
- **不受影响**：`TYPE_DEL` 路径已跳过；`TYPE_UPDATE` 走 `backup_file_block:535`；全量备份。

## 5. 处置建议（分级，不改代码）

### 5.1 短期规避（运维可立即执行，无需发版）

1. **探测前过滤**：在触发增量前于源机预检 `ls -ld /var/lib/greatdb-cluster/datanode1/mount_verify_*`，若存在则等待其消失或手动 `rmdir` 空目录后再触发；`DISK_CHECK*` 同理（已大多为 `TYPE_DEL`）。
2. **错峰触发**：避开 GreatDB 集群的挂载校验窗口（本次时间戳 `20260902` 提示与日期强相关），将增量窗口后移。
3. **重跑即恢复**：本次线程池中 `binlog.*` 已成功，下次增量将基于更新的 `FsMeta` 快照重枚举，已消失的临时目录将转为 `TYPE_DEL` 被跳过，无需全量重建。

### 5.2 长期修复建议（需发版，附接缝与验证，仅建议不落地）

- **接缝** `fs-backup/fsclient/transfer_file.cpp:435` `backup_new_directory`：新增 `is_ephemeral_dir(path)` 判 `mount_verify*`/`DISK_CHECK*` 前缀；当 `rpc_conn_cli_readdir_tree` 返回 `ENOENT/ENOTDIR/IO_EOF(-3)` 时对命中前缀的路径 `WarningLog` 并返回 0 跳过，其余仍返回 -1 中断。
- **接缝** `rpc/rpc.cpp:1986,2024`：当 `ret==-3` 时显式打印 `IO_EOF(ret=-3)` 而非 `strerror(errno)`，并在调用侧保存 `errno` 副本避免污染。
- **备选**：将临时前缀纳入 `fs_source.cpp:850` 的 `exclude-dir` 配置化，避免硬编码；但需评估与全量 `excludes` 的一致性。
- **验证**：`xmake build` 零告警；`xmake test` 32/32；补充 9 场景用例（临时+ENOENT/ENOTDIR/IO_EOF→skip，非临时+ENOENT→不 skip，EACCES→不 skip）。

## 6. 验证方法（读报告者可复跑）

```bash
grep -n "backup_new_directory\|PathForEachCallback\|TransferIncrementData" fs-backup/fsclient/transfer_file.cpp
grep -n "rpc_conn_cli_readdir_tree" rpc/rpc.cpp
grep -n "dir_traversal_at\|rpc_conn_srv_readdir_tree" rpc/rpc-server.cpp libs/dir_utils.c
grep -n "mkdir_path" libs/common.c
# 日志关键字
grep "mount_verify\|DISK_CHECK\|File exists.*17\|ret=-3\|PathForEachCallback failed" <log>
```

## 7. 结论

本次为“短命临时目录在快照与拉取间消失”触发的必现型增量中断，`EEXIST` 为噪音，`IO_EOF(-3)` 为信号；链路未做“消失即跳过”容错是主因。按 §5.1 即可不改代码规避；长期按 §5.2 发版后可彻底容错且不掩盖真实缺失。

