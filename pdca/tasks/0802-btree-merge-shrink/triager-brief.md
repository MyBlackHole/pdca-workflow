# T0204 Triage Brief：btree merge（前台合并/键下移合并，树收缩）

## 任务概述

subvol btree 域已覆盖分裂（叶子/内部/根，interior.rs:380 split_leaf
up-level 循环）、迭代、键更新，但 **merge 完全缺失**：本地 bcachefs
`fs/btree/interior.c` 的 `__bch2_foreground_maybe_merge`(2907) +
`btree_merge` N→M 合并管线在 subvol 无对应（`sib_u64s` 只维护不
消费）。后果：**大量删除后树永不收缩**（深度只增、节点只减不合并、
"删除 btree 节点"路径不存在）——这是四域（btree/事务/journal/间接
数据）审计中唯一的实质性核心逻辑缺口（T0203 归档后的完整性审计结论）。

## 上游锚点（AC-1 将逐段对照）

- `interior.c:2907 __bch2_foreground_maybe_merge`：合并入口——门槛
  （min/max_key 边界 + shard boundary + sib_u64s 阈值）、srcs 集合
  构建（prev 兄弟/自身/next 兄弟，左到右排序）、估算门控
  `compute_merge`（nr_dsts < srcs.nr 才合并）、should_be_locked 补
  fill/丢弃、parent 一致性校验、`btree_merge_topology_check`(2399)。
- `interior.c:2447 btree_merge_push_pos`：兄弟键推入 srcs（含格式感知
  估算）。`interior.c:2577/2591 merge_fail_reset_sib_u64s`：失败回滚
  （sib_u64s 置 U16_MAX 防反复尝试）。
- N→M 合并管线：`compute_merge` → `btree_pack_into_dsts`/`sort_into`
  （键重新打包到 dst 节点）→ interior 更新提交（删除空源节点 +
  parent pivot 更新，subvol 对应 `trans_commit_pending_interior`
  update.rs:2219 + `retire_node` interior.rs:596 已有 split 版可复用）。
- 三个调用点：`commit.c:1023 trans_commit_merge`（常规 commit 路径，
  `(*ip)->flags & BCH_TRANS_COMMIT_...` 门控）、`interior.c:2314`
  （split 后逐层对 intent-locked 父节点尝试）、`interior.c:3369`
  （node_merge_key 后）。

## 方案

1. AC-1 逐段对照 interior.c merge 管线 + commit.c 调用点，落盘锚点。
2. subvol 实现（interior.rs 或新模块）：合并可行性估算（sib_u64s
   消费 + 格式感知 repack 门控）、N→M 键打包、空节点删除 +
   parent pivot 更新（复用既有 interior 更新提交设施）、失败回滚
   （防反复尝试）。
3. 调用点挂载：split 后逐层尝试合并 + commit 路径合并（对齐
   trans_commit_merge 门控）。
4. 属性测试：删除压力（大量 delete 后树收缩——深度不增、节点数
   减少、pivot/拓扑不变量）、崩溃恢复后拓扑有效、与既有
   split_stress/random_operations 模型不冲突（现有模型是逻辑键级，
   不受物理节点布局影响，但需要新增物理拓扑断言）。
5. 全量回归（--test-threads=4 基线）。

## 范围外

GC、stripe/EC、btree_node_rewrite（设计替代已论证）、写缓冲
（write buffer）合并。
