## 当前状态

T0181 已获 confirmed verdict，正在 Act 归档。它只定义 physical pointer 与派生状态的
持久化/恢复合约，未修改 subvol 产品代码。

## 未完成事项

T0182 仍在 Plan，负责 transaction trigger runner、sort-order/multi-round 和
extent/btree-pointer dispatch。T0183 等待 T0182 完成后实施派生 writer/rebuild/validator。

## 已知约束

本地 bcachefs 源码是唯一语义依据。physical pointer 是权威主数据；alloc/backpointer/
accounting 是派生状态。`BTREE_TRIGGER_norun` replay 后必须先扫描重建、验证集合，再发布
派生查询。GC/stripe 不得以占位逻辑进入后续任务。

## 推荐的下一步

从 T0182 的 Plan 签审开始，先证明 split pointer 的最终持久化入口，再接入 runner；
不要提前实现 alloc/backpointer writer。

## 关键上下文文件列表

- `pdca/tasks/0802-transaction-trigger-runner-pointer-dispatch/prd.md`
- `pdca/tasks/archive/2026-08/0802-physical-pointer-derived-state-contract/design.md`
- `records/T0181-0802-physical-pointer-derived-state-contract/conclusion.md`
- `knowledge/core/recovery-derived-state-publication-gate.md`

## Suggested skills

- `flow-plan`
- `research`
- `verify-convergence`
