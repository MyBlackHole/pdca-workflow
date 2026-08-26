---
schema: pdca.asset/v1
id: T3974-0826-squash-last-six-commits
phase: check
source_ids: [squash-verify]
---

## 上下文

分支 `6.2.0.0/F/139` 最近六个提交（TLS/mTLS 整合、rpc 安全开关、oss HTTPS 开关化/单测、tls-keygen SAN 修复）需压缩为单个提交。用户决策：综合提交信息；仅本地改写不推送。

## 假设与结果

- 假设：`reset --soft HEAD~6 + 重新提交` 能在不改变最终树内容的前提下将六提交合一。
- 结果：成立。新提交 `0ec03d3d`，父提交 `fe9d4364`，树哈希与合并前完全相同。

## 分析

Check 阶段独立复核（非复用 Do 输出），以树哈希对比替代 diff 空输出作为更强证明：

- **AC-1** ✅ `git log --oneline -1` 显示唯一合并提交 `0ec03d3d`，信息为用户确认的综合版本（squash-verify）
- **AC-2** ✅ `backup/pre-squash-T3974^{tree}` 与 `HEAD^{tree}` 哈希同为 `6f0deec5c54d941c32281ffcb3a0c96004fc0d19`，逐字节一致（squash-verify）
- **AC-3** ✅ HEAD 父哈希 = `fe9d4364748b…`，原六提交已不在分支历史（squash-verify）
- **AC-4** ✅ 工作区干净；全程未 push，`origin/6.2.0.0/F/139` 仍指 `4ef9c5c1`（squash-verify）

## 适用边界

- 结论仅适用于线性历史上连续 N 个头部提交的 squash；不适用于分支间 merge --squash 场景。
- 远程历史未改写：本地与 origin 自 `fe9d4364` 分叉，任何后续 push 必须 `--force-with-lease` 且会覆盖远程的 `4ef9c5c1`。

## 下一轮建议

- 用户确认远程更新后可删除备份引用 `backup/pre-squash-T3974`。
- 同类 git 维护操作可复用本任务模式：备份引用 → soft reset → 断言树哈希一致。
