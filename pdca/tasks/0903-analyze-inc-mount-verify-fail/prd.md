# 增量备份 mount_verify 临时目录导致 EEXIST 失败根因分析

## 背景

生产环境 2026-09-02 增量备份失败，关键日志如下：

```
[2026-09-02 18:06:06,287]|Info|fs-backup/fsclient/transfer_file.cpp:445 backup_new_directory: /mount_verify_20260902 (remote: /var/lib/greatdb-cluster/datanode1/mount_verify_20260902)
[2026-09-02 18:06:06,287]|Error|rpc/rpc.cpp:1988 rpc_conn_cli_readdir_tree|140030930913088| recv response failure. File exists(errno: 17)
[2026-09-02 18:06:06,287]|Error|fs-backup/fsclient/transfer_file.cpp:456 backup_new_directory: readdir_tree /var/lib/greatdb-cluster/datanode1/mount_verify_20260902 failed, ret=-3
[2026-09-02 18:06:06,287]|Error|fs-backup/fsclient/transfer_file.cpp:491 fs_path_callback|140030930913088| backup_new_directory /mount_verify_20260902 failed
PathForEachCallback failed
TransferTargetPath failed
```

增量路径为 `TransferIncrementData`（`transfer_file.cpp:551`）经 `FsMeta::PathForEachCallback:779` 遍历 `TYPE_NEW|S_ISDIR` 的路径，对 `/mount_verify_20260902` 调用 `backup_new_directory` 再经 `rpc_conn_cli_readdir_tree:1958` 拉取远端目录。此失败导致后续 `TransferTargetPath` 整体中断，尽管线程池中已有 binlog 等文件的 `scp download` 仍在并发完成。

本次为纯分析任务，不修改业务代码，仅输出根因与处置建议。

## 目标

- 定位本次 `mount_verify_20260902` 触发 `File exists`/`ret=-3(IO_EOF)` 到 `PathForEachCallback failed` 的完整证据链与根因分级
- 给出不改代码的短期规避与长期处置建议，并明确接缝与验证方法

## 范围

- 输入：上述日志、`fs-backup/fsclient/transfer_file.cpp`、`rpc/rpc.cpp`、`rpc/rpc-server.cpp:3069`、`libs/dir_utils.c`、`libs/common.c:71`
- 不做：不修改 `transfer_file.cpp`/`rpc.cpp` 等业务代码，不提交代码修复

## 分析方法

1. 日志与代码走读交叉验证
2. `dir_traversal_at` → `rpc_conn_srv_readdir_tree` → `rpc_conn_cli_readdir_tree` 协议与错误码追踪
3. `errno` 污染与 `IO_EOF=-3` 分支假设验证

## 验收标准

- [ ] AC-1 已产出带行号引用的根因报告：明确直接诱因、链路因、污染因，并区分 `EEXIST(17)` 与 `IO_EOF(-3)` 的真实含义
- [ ] AC-2 已给出分级处置建议：短期规避（不改代码可执行）与长期修复建议（含接缝与验证方法），且与证据链一致
- [ ] AC-3 报告已登记为证据且 `convergence` 回链，`validate-convergence` 通过

## 关联本体节点

```
ontology:domain/backup
ontology:concept/failure-mode
ontology:concept/pdca-task
```

## 拆分映射

- 证据链与根因分级 -> ontology:domain/backup
- 处置建议与验证方法 -> ontology:concept/failure-mode

## 风险与对策

- 风险：过度容错建议掩盖真实缺失。对策：建议中明确仅临时前缀 + ENOENT/ENOTDIR/IO_EOF 可跳过，其余保持失败

