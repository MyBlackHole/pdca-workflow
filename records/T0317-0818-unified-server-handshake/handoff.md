## 当前状态

T0317 已完成实现、全量测试、Check confirmed，Act 处置为 task_only，待归档。

## 未完成事项

无。归档后如扩展算法，需重新建立任务范围。

## 已知约束

不新增 CLI 参数、不修改协议字段、不改变 `ca_cn` 证书选择；工具使用各自现有配置转换为握手参数。

## 推荐的下一步

仅在新增算法或接入新工具时创建后续任务，并重新确认参数和测试范围。

## 关键上下文文件列表

- `records/T0317-0818-unified-server-handshake/conclusion.md`
- `pdca/tasks/0818-unified-server-handshake/prd.md`
- 项目提交 `61cf4509`、`d80ea57e`

## suggested skills

- `register-evidence`
- `verify-convergence`
- `write-conclusion`
