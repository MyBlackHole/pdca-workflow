# T0204 btree merge（前台合并/键下移合并，树收缩）

## 问题陈述

完整性审计（T0203 归档后）结论：subvol btree 域唯一实质性核心缺口是
**merge 缺失**。bcachefs 常规提交路径包含前台合并
（`__bch2_foreground_maybe_merge`，interior.c:2907，经
`trans_commit_merge` commit.c:1023 与 split 后路径 interior.c:2314
调用），subvol 无对应——`sib_u64s` 只维护不消费，大量删除后树永不
收缩（深度只增、节点只减不合并、"删除 btree 节点"路径不存在）。

## 目标

对齐 bcachefs 前台合并语义实现 subvol 的 btree merge：相邻节点
（prev/自身/next，可合并方向）在键量低于阈值时合并为一个节点，
删除空节点并更新 parent pivot；失败回滚防反复尝试。树在删除压力下
能收缩（深度不增、节点数减少），且崩溃恢复后拓扑有效。

## 验收标准

- [ ] AC-1: 修改前逐段对照本地 bcachefs merge 管线（interior.c
       `__bch2_foreground_maybe_merge` 2907 / `btree_merge_push_pos`
       2447 / `btree_merge_topology_check` 2399 /
       `merge_fail_reset_sib_u64s` 2591 / N→M 打包管线与
       `trans_commit_merge` commit.c:1023 调用点），记录锚点与
       subvol 域内差异判定。
- [ ] AC-2: 合并实现：可行性估算（sib_u64s 消费 + 格式感知 repack
       门控，对齐 compute_merge 估算→精确路径）、N→M 键打包合并、
       空节点删除 + parent pivot 更新（复用 interior 更新提交设施）、
       失败回滚（sib_u64s 置 U16_MAX 防反复尝试）。
- [ ] AC-3: 调用点挂载：split 后逐层尝试合并（对齐 interior.c:2314）
       与 commit 路径合并（对齐 trans_commit_merge 门控），行为与
       bcachefs 控制流一致。
- [ ] AC-4: 删除压力属性测试：大量 delete 后树收缩（深度不增、
       节点数减少、pivot/拓扑不变量）；崩溃恢复后拓扑有效；
       与既有模型（split_stress/random_operations 逻辑键级模型）
       不冲突。
- [ ] AC-5: 定向、故障/属性和全量 workspace 测试通过，单项不超过
       一分钟（验证基线 --test-threads=4）。

## 范围外

GC、stripe/EC、btree_node_rewrite（设计替代已论证：journal-first
持久化 + __bch2_btree_node_write）、写缓冲（write buffer）合并、
快照子树合并/删除。

## 备注

复用：interior.rs:380 split_leaf 的 up-level 循环设施（节点分配、
interior 更新提交 trans_commit_pending_interior update.rs:2219、
retire_node interior.rs:596）、sib_u64s 字段（interior.rs:338 已有
维护点）、拓扑校验 bch2_btree_node_check_topology（interior.rs:256）。
