---
schema: pdca.asset/v1
id: T0182
phase: check
source_ids: [source-audit, verification, code-review, convergence-map]
---

## 上下文

T0182 合并了 transaction trigger runner、physical pointer 的 alloc/backpointer 派生维护、
interior publication 与恢复重建；不包含 allocator、GC、stripe、LRU 或 VFS。

## 假设与结果

结论候选：已确认范围内的单格式 storage core 满足 PRD AC-1 至 AC-6。

- local bcachefs `commit.c`、`buckets.c`、`backpointers.h`、`interior.c`、`recovery.c`
  和 members 代码均已作源码锚定；
- online/member/geometry admission、transactional old/new pointer dispatch、norun replay、
  alloc/backpointer rebuild 和 interior journal publication 均由确定性测试覆盖；
- 184 个单测与 10 个属性测试通过，fmt/diff 检查通过；收敛验证为 `valid: true`。

## 分析

primary pointer 是恢复权威状态。replay 不运行 trigger；派生树仅在 replay 完成后清空并
从 primary scan 重建。physical interior pointer 先完成新节点写入，再在单独事务中依次记录
old overwrite 与 new btree/root entry，避免 split restart 在错误边界提前发布。

## 失败原因（仅 rejected/partial）

不适用；当前结论候选为 confirmed。

## 适用边界

结论仅适用于该仓库的单格式、单设备 members-v2 geometry 和当前 engine-local btree id
集合。它不声称实现了 bcachefs 的完整 allocator、GC、stripe、LRU、fsck 或 VFS 语义。
严格 clippy 仍受工作区既有 224 项 warning 基线影响，未作为本 PRD gate。

## 下一轮建议

若引入多设备或 allocator，先在 Plan 阶段扩展 device attach、open-bucket 生命周期和
accounting/GC 的完整上游对照，再新增 crash/property 覆盖。
