---
name: write-journal
description: Append a task summary or daily note to pdca/journal/YYYY-MM-DD.md. Use when closing a task (flow-act) or when the user says "写日志" / "记日志".
---

# Write Journal

Append a lightweight entry to `$PDCA_HOME/pdca/journal/YYYY-MM-DD.md`（不存在则创建）。

## Mode A: Task Close（flow-act 自动调用）
先检查 `task.json` 中 `meta.disposition` 是否存在。不存在则终止，提示"请先完成 flow-act 步骤 3（记录处置）后再写日志"。

通过后从当前任务提取以下信息追加到当日日志：

```markdown
## 任务进度
- <task-id>: <任务标题> [<阶段>→<目标阶段>]

## 关键决策
- <本任务中产生的关键决策>

## 阻塞项
- <如无则写"无">
```

## Mode B: Manual（用户说"写日志"时）
1. 采集用户输入：今天做了什么、有什么决策、阻塞
2. 按格式追加到当日日志

## 格式维护
- 已有当日日志 → 追加到末尾
- 无当日日志 → 创建文件，以 `# YYYY-MM-DD` 开头
- 不要覆盖之前的内容

## 已知坑

- 已有当日日志必须**追加**到末尾，不得覆盖历史内容（T0264）。
- 无当日日志时创建文件须以 `# YYYY-MM-DD` 开头。
