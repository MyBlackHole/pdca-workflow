---
name: resolving-merge-conflicts
description: Resolve in-progress git merge/rebase conflicts by intent — find the primary source, preserve both intents per hunk, never abort, then run automated checks. Use when git merge or rebase reports conflicts.
---

# Resolving Merge Conflicts — intent-based

系统化解析 merge/rebase 冲突：**按意图解析**，而非策略表。目标是保留双方的原始意图，
绝不中途放弃（`--abort`），解析完成后跑项目自动化检查修复 merge 破坏。

## Process

### 1. 看当前状态

- 运行 `git diff --name-only --diff-filter=U` 列出冲突文件；`git status` 看 unmerged paths。
- 确认 merge/rebase 进行中的整体目标（是合并哪个分支、为何合并）。

### 2. 找 primary source（理解意图）

对每个冲突，理解每侧**为什么**做了这个改动、原始意图是什么：

- 读相关 commit message（`git log -p`、`git log --oneline -- <file>`）
- 查对应 PR / issue / ticket 上下文
- 关键问题：这侧改动想解决什么？被合并分支的目标是什么？

### 3. 逐 hunk 解析——保留双方意图

对每个冲突块：

- **尽量保留双方意图**：两侧改动都有价值时合并两者，都写进结果。
- **不兼容时**：选择符合 merge 目标的那一侧，并**记录权衡**（在代码注释或 merge commit message 中说明另一侧意图为何未采纳）。
- **绝不发明新行为**：不写两侧都没表达过的逻辑。
- **绝不 `--abort`**：merge 冲突是状态不是错误，abort 会丢弃已解析工作。
- 同一文件内不同 hunk 可不同处理；`git checkout --ours/--theirs <file>` 仅当文件全部 hunk 用同一策略时才用。
- 涉及 generated/lock 文件时优先 theirs（解析后重新生成）。

### 4. 跑自动化检查并修复

解析完成后，发现并运行项目的自动化检查——通常顺序为 **typecheck → tests → format**：

```bash
git diff --check          # 无残留冲突标记
<typecheck>               # 如 mypy / tsc
<test suite>              # 项目测试
<format>                  # 如 ruff format / prettier
```

修复任何 merge 破坏的（被 `git diff --check` 捕获的标记、类型错、测试失败）。

### 5. 完成 merge/rebase

- stage 全部 + commit；rebase 则 `git rebase --continue` 直到全部 commit 处理完。
- 有保留意图说明时写入 merge commit message。

## Rules

1. **绝不 `--abort`**——除非用户明确要求放弃整个 merge 并接受数据丢弃。
2. **保留双方意图**优先；取舍必须记录。
3. 不发明新行为。
4. 解析后**必须**跑 typecheck/tests/format 并修复破坏。
5. 不确定的 hunk 标注 `// TODO: resolve — <file>:<line>` 留给人工，不静默猜测。
