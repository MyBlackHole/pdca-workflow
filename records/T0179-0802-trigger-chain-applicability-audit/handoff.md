## 当前状态

T0179 已在 partial verdict 下进入 Act：原审计仅对公开 cookie/deleted 与 snapshot
atomic 路径有效，不能代表完整存储引擎 core。

## 未完成事项

由 T0180 完成 extent、alloc、内部 btree pointer、backpointer/stripe-backpointer、
accounting、journal/recovery 与 GC 的完整 trigger 依赖审计；在该审计前不得实现
通用 transactional/GC runner。

## 已知约束

仅以 `/home/black/Documents/bcachefs-tools/fs` 为语义依据；subvol btree-id 独立，
不得直接复制 fs 层 btree-id 编号或未证明适用的路径。

## 推荐的下一步

完成 T0180 Plan 终审后，先建立依赖图和可达性证据，再按独立、最小验证范围创建
后续实现任务。

## 关键上下文文件列表

- `pdca/tasks/0802-extent-alloc-btree-backpointer-trigger-audit/prd.md`
- `records/T0179-0802-trigger-chain-applicability-audit/conclusion.md`
- `knowledge/core/trigger-audit-derived-state-boundary.md`

## Suggested skills

- `research`
- `register-evidence`
- `verify-convergence`
- `write-conclusion`
