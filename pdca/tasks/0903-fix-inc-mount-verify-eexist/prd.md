# 修复增量备份遇到 mount_verify 临时目录时 EEXIST 失败导致整体备份中断

## 背景

生产环境 2026-09-02 增量备份失败，日志显示：

```
[2026-09-02 18:06:06,287]|Info|fs-backup/fsclient/transfer_file.cpp:445 backup_new_directory: /mount_verify_20260902 (remote: /var/lib/greatdb-cluster/datanode1/mount_verify_20260902)
[2026-09-02 18:06:06,287]|Error|rpc/rpc.cpp:1988 rpc_conn_cli_readdir_tree|140030930913088| recv response failure. File exists(errno: 17)
[2026-09-02 18:06:06,287]|Error|fs-backup/fsclient/transfer_file.cpp:456 backup_new_directory: readdir_tree /var/lib/greatdb-cluster/datanode1/mount_verify_20260902 failed, ret=-3
[2026-09-02 18:06:06,287]|Error|fs-backup/fsclient/transfer_file.cpp:491 fs_path_callback|140030930913088| backup_new_directory /mount_verify_20260902 failed
PathForEachCallback failed
TransferTargetPath failed
```

增量备份通过 `FsMeta::PathForEachCallback` 遍历 meta 中的路径变更，`fs_path_callback` 对 `TYPE_NEW` 且 `S_ISDIR` 的路径调用 `backup_new_directory`，该函数本地 `mkdir_path` 后通过 `rpc_conn_cli_readdir_tree` 递归拉取远端目录内容。若此时远端目录为临时验证目录（如 GreatDB 集群的 `mount_verify_20260902`），可能在 meta 快照与实际拉取之间已被删除/卸载或处于不一致状态，导致 `dir_traversal_at` 失败、连接异常及 `ret=-3 (IO_EOF)`，且因未区分"可容忍的临时目录消失"与"真实错误"，直接使 `PathForEachCallback` 返回 -1，中断整个增量备份。

## 目标

使增量备份对"远端新建目录在拉取时已消失/不可读"的场景具备容错能力：对 `mount_verify_*`、`DISK_CHECK*` 等临时目录的 `readdir_tree` 失败按"跳过"处理，不中断整体 `TransferIncrementData`；同时保持对真实目录错误的可见性。

## 功能需求

1. **容错的 backup_new_directory**：当 `rpc_conn_cli_readdir_tree` 失败且 errno 为 `ENOENT/ENOTDIR` 或 ret 为 `IO_EOF` 时，若路径命中临时目录模式（`mount_verify*`、`DISK_CHECK*` 前缀），记录 Warning 并返回 0（跳过），而非 -1 中断回调链。
2. **调用侧区分**：`fs_path_callback` 中对 `backup_new_directory` 的失败需区分"可跳过"与"不可跳过"，仅不可跳过时设置 `*ctx->ret = -1` 并返回 -1 终止遍历；可跳过时仅 Warning 并返回 0 继续。
3. **连接隔离**：确认 `dir_rpc_conn` 为单线程串行使用，不受线程池并发影响；若 `rpc_conn_is_ready_recv_msg` 返回 `IO_EOF`，需正确打印 ret 而非复用 stale errno。

## 非功能需求

- 不改变全量备份路径（`full_bak=true` 时走 `rpc_download_file`，不受影响）
- 回归现有 `fs-backup` 单测与 `rpc` 相关测试

## 验收标准

- [ ] AC-1 增量备份遇到远端 `mount_verify_*` 目录在 `readdir_tree` 时返回 ENOENT/IO_EOF，不再导致 `PathForEachCallback failed` 与 `TransferTargetPath failed`，整体备份标记成功
- [ ] AC-2 回归测试覆盖：新增 `transfer_file` 单元测试模拟 `rpc_conn_cli_readdir_tree` 对临时目录返回 ENOENT，验证 `backup_new_directory` 返回 0 且上级回调继续；对非临时目录的 ENOENT 仍返回 -1
- [ ] AC-3 存量 `fs_meta` 与 `dir_utils` 单测通过，`xmake build` 无新增告警

## 关联本体节点

```
ontology:domain/backup
ontology:concept/failure-mode
ontology:concept/pdca-task
```

## 拆分映射

- 容错的 backup_new_directory 与临时目录判别 -> ontology:domain/backup
- 调用侧区分与连接错误修正 -> ontology:concept/failure-mode

## 风险与对策

- 风险：过度容错掩盖真实备份缺失。对策：仅对 `mount_verify*`/`DISK_CHECK*` 前缀 + ENOENT/IO_EOF 组合放行，其余仍失败；放行时 Warning 日志含路径与 ret/errno 便于审计
- 风险：errno 污染导致误判。对策：readdir_tree 失败分支显式读取 `errno` 前先保存，或以 `ret` 区分 IO_EOF

## 开放问题

- 是否需将临时目录前缀做成可配置的 exclude 列表而非硬编码？本期先硬编码前缀，配置化待后续评估

