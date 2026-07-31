## 当前状态

T0142 已完成实现、证据登记、Check 结论确认和 Act 知识处置，等待归档。

## 未完成事项

无实现事项；仅需通过 archive 门禁并移动任务目录。

## 已知约束

- 清理只适用于 `pdca/tasks/` 的无效直接子目录。
- 恢复源固定为预删除 commit `4582c0c9e6e43f3184b322239a27f5010a066649`。
- 恢复旧目录会重新引入严格 schema 错误。
- 不增加旧格式兼容或迁移副本。

## 推荐的下一步

独立评估 research 来源链 validator；必须先证明它能改变现有错误判断，不与本任务的删除逻辑耦合。

## 关键上下文文件列表

- `scripts/audit-history.py`
- `records/R0142-clean-invalid-active-history/conclusion.md`
- `records/R0142-clean-invalid-active-history/evidence/manifest.jsonl`
- `knowledge/pdca-flow/destructive-cleanup-safety.md`

## Suggested skills

- `flow-plan`
- `grilling`
- `register-evidence`
- `verify-convergence`
- `advance-phase`
