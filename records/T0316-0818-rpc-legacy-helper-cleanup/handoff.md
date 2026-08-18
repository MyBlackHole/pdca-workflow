## 当前状态

T0316 已完成实现、Check verdict confirmed，正在 Act 的归档收尾阶段。

## 未完成事项

无。`tls_cert_verify_is_local` 的公共 ABI 删除评估留待独立任务。

## 已知约束

不得删除仓库外可能使用的公共 API；RPC/rdbcomm 当前 TLS session I/O 和协议保持不变；RPC/fs-backup 中仍使用的公共 `rpc_send/rpc_recv` 不属于本任务。

## 推荐的下一步

完成 T0316 归档；若需要删除 `tls_cert_verify_is_local`，先做 ABI 影响评估。

## 关键上下文文件列表

- `records/T0316-0818-rpc-legacy-helper-cleanup/conclusion.md`
- `pdca/tasks/0818-rpc-legacy-helper-cleanup/prd.md`
- 项目提交 `af7134be`

## Suggested skills

- `register-evidence`
- `verify-convergence`
