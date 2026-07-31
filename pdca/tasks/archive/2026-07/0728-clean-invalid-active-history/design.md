# T0142 设计

## Scope 边界

| scope | dry-run 候选 | apply 允许边界 |
|------|--------------|----------------|
| `active` | `pdca/tasks/*/task.json` 的直接父目录，排除 `archive`，且严格校验失败 | `target.parent == pdca/tasks` 且 `target.name != archive` |
| `archive` | `pdca/tasks/archive/**/task.json` 的父目录，且严格校验失败 | 位于 archive 下且不等于 archive 根 |

两个 scope 均继续拒绝通配符、受保护前缀、目录缺失、digest 漂移、确认数量错误和默认不可恢复目标。

## Manifest 合约

现有 `pdca.deletion-manifest/v1` 增加必填：

```json
{"scope": "active"}
```

apply 不接受缺少或未知 scope 的 manifest。每个 target 保持具体路径、目录 digest、tracked/total 文件数、Git recoverability、失败原因与恢复命令。

## 原子性边界

apply 在删除前先完成所有目标的路径、存在性、digest 和 recoverability 预检。文件系统递归删除本身不是跨目录事务，但本轮所有目标均由 Git 完整跟踪，任何已删除目录都能按 manifest recovery 命令恢复。

## 保护资产验证

执行前计算以下目录的确定性摘要，执行后再次比较：

- `records/`
- `knowledge/`
- `pdca/journal/`
- `pdca/tasks/archive/`
- 本任务目录

## 保留理由

active scope 有当前真实消费者，并把未来严格 schema 污染的清理纳入相同安全门禁；它不是旧格式兼容逻辑，也不解析旧数据。
