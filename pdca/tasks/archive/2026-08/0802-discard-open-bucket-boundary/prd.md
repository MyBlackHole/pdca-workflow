# T0189 discard 边界与 open-bucket 回收保护

## 问题陈述

T0187/T0188 已实现最小 bucket reclaim 与公开 API 验证，但当前 `need_discard → free`
仍由简化调用直接推进，尚未表达本地 bcachefs discard.c 的 journal boundary、设备可写、
discard capability 与 open-bucket 保护条件。

## 目标

严格依据本地 discard.c/background.c，补齐最小 discard 前置条件、need_discard 派生索引和
open-bucket 保护，并以故障/重启测试验证不会过早复用 bucket。

## 验收标准

- [ ] AC-1: 修改前逐段记录 discard.c 的 `__discard_mark_free`、open bucket、journal boundary、设备可写与重试分支源码锚点。
- [ ] AC-2: 只有 need_discard、journal boundary 满足、设备可写且无 open/live dirty reference 时才允许转 free。
- [ ] AC-3: alloc、need_discard/freespace 索引与 generation 更新保持同一 transaction，失败不产生半状态。
- [ ] AC-4: discard worker/受控调用覆盖 EEXIST/EAGAIN、JournalWrite、TransactionRestart 与 process-style restart。
- [ ] AC-5: deterministic 与属性模型验证 bucket 不会在 open/live/discard 未完成时被复用。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 先实现 engine-local 的最小 discard boundary seam，复用现有 fault points 与 T0188 模型。
- 不实现设备真实 TRIM I/O；用确定性状态/回调模拟本地 discard.c 的提交边界。
- 不扩展完整 GC、LRU、stripe/EC、VFS 或旧格式迁移。

## 范围外

真实 block-device discard、完整后台调度策略、open bucket worker 全量并发模型、GC/LRU、stripe/EC、VFS。

## 备注

前置：T0187、T0188 已归档；本任务仅承接其明确遗留的 discard/open-bucket 边界。
