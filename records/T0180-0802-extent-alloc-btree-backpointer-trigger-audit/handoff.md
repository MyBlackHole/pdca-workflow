## 当前状态

T0180 已在 Check 获得 confirmed verdict，Act 正在归档。未修改 subvol 产品代码。

## 未完成事项

按顺序处理 Plan 中的 T0181、T0182、T0183；均尚未进入 Do。GC 不在这些任务的范围内。

## 已知约束

本地 `/home/black/Documents/bcachefs-tools/fs` 是唯一语义依据；任何产品改动前必须先读
对应源码。公开 StorageEngine 仍使用 `BTREE_ITER_not_extents`；不能将审计结论写成现有
cookie 数据已损坏。journal replay 的 `BTREE_TRIGGER_norun` 要求未来显式恢复合约。

## 推荐的下一步

从 T0181 Plan 签审开始，先固定单一格式 physical pointer 与派生状态恢复合约；不要跳过
它直接实现 runner 或 backpointer。

## 关键上下文文件列表

- `pdca/tasks/0802-physical-pointer-derived-state-contract/prd.md`
- `pdca/tasks/0802-transaction-trigger-runner-pointer-dispatch/prd.md`
- `pdca/tasks/0802-alloc-backpointer-derived-recovery/prd.md`
- `records/T0180-0802-extent-alloc-btree-backpointer-trigger-audit/conclusion.md`
- `knowledge/core/physical-pointer-derived-state-recovery-boundary.md`

## Suggested skills

- `flow-plan`
- `research`
- `verify-convergence`
