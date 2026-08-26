# 合并分支头部连续提交（squash head commits）

## 模式

线性历史上合并最近 N 个提交为单个提交的安全三步法：

```bash
git branch backup/pre-squash-<task>        # 1. 备份引用，防回退
git reset --soft HEAD~N                    # 2. 变更收敛到暂存区
git commit -m "<综合信息>"                  # 3. 一次性重提交
```

## 验证（树哈希断言）

比 `git diff` 空输出更强的逐字节一致证明——内容寻址下树哈希相同即内容完全相同：

```bash
git rev-parse backup/pre-squash-<task>^{tree} HEAD^{tree}   # 两值必须相同
```

## 边界与风险

- 仅适用于**头部连续**提交；中部提交需 `rebase -i`，分支间合并用 `merge --squash`。
- 若待合并区间包含**已推送提交**，squash 后本地与 origin 自分叉点分叉，push 必须 `--force-with-lease` 且会覆盖远程历史；若他人基于旧远程历史工作会受影响。
- 备份分支在用户确认远程更新后再删除。

## 来源

T3974（2026-08-26）：六提交合一为 `0ec03d3d`，树哈希 `6f0deec5` 双侧一致验证通过。
