---
name: flow-act
description: |
  改进阶段执行流。从结论记录到知识积累和归档。
  覆盖知识沉淀、处置记录、架构改进、跨会话桥接。
---

# 改进阶段执行流（PDCA — Act）

## 入口条件
- `task.json` 的 `meta.phase` 为 `act`
- `$PDCA_HOME/records/<record-id>/conclusion.md` 存在（Check 阶段产物）

## 步骤总览

| 步骤 | 内容 |
|------|------|
| Ac0 | 读取 Verdict — 分支 confirmed/rejected/partial |
| Ac1 | Grill（仅 confirmed） |
| Ac2 | 知识沉淀（仅 confirmed） |
| Ac2a | 失败处置（仅 rejected） |
| Ac2b | 部分沉淀 + 跟进（仅 partial） |
| Ac3 | 记录处置 |
| Ac4 | 架构改进 |
| Ac5 | 跨会话桥接（Handoff） |
| Ac6 | 追加日志 |
| Ac7 | 提交（含 disposition） |
| Ac8 | 归档 |

## 步骤

### Ac0. 读取 Verdict
读取 `task.json` 的 `meta.verdict.outcome`（confirmed | rejected | partial），按 verdict 分支执行。

**confirmed** → 走完整路径（步骤 1-8）
**rejected** → 跳到步骤 2a（仅失败处置）
**partial** → 跳到步骤 2b（部分沉淀 + 跟进）

---

### Ac1. Grill（仅 confirmed）
加载 `$PDCA_HOME/skills/grilling/SKILL.md`，追问知识沉淀质量：
- 这个结论的适用范围和限制是什么？
- 哪些部分可以提炼为可复用的知识？
- 下次遇到类似问题，流程上有什么改进？

追加 Q&A 到 `clarifications.jsonl`（`source: "grilling"`）。

### Ac2. 知识沉淀（仅 confirmed）
将可复用的洞察写入 `$PDCA_HOME/knowledge/<topic>/<slug>.md`。
不满足复用标准的不写，record 本身即为归档。

无论是否产出知识，在 `clarifications.jsonl` 追加一条记录：
```json
{"source": "knowledge_decision", "at": "<ISO 时间戳>", "action": "wrote|skipped", "reason": "<复用理由或跳过理由>"}
```

写入知识后还需在 `$PDCA_HOME/knowledge/manifest.jsonl` 追加一行：
```json
{"version":1,"revision":1,"at":"<ISO 时间戳>","knowledge":"<topic>/<slug>.md","knowledge_digest":"sha256:<文件 sha256>","source_record":"records/<record-id>/conclusion.md","source_digest":"sha256:<source sha256>","reason":"<复用理由>"}
```

### Ac2a. 失败处置（仅 rejected，跳过步骤 Ac1）
结论不成立时，不做知识沉淀。从 `conclusion.md` 的"失败原因"章节提取教训，写入日志即可。

跳过步骤 Ac3–Ac5（无需知识沉淀、架构改进、handoff），直接跳到步骤 Ac6（日志）。

### Ac2b. 部分沉淀 + 跟进（仅 partial，跳过步骤 Ac1）
结论部分成立时：
1. 仅沉淀确凿可复用的部分到 `$PDCA_HOME/knowledge/<topic>/<slug>.md`
2. 创建跟进任务处理未完成部分（在 `pdca/tasks/` 下创建新任务，`title` 中包含"跟进"标记，`meta.phase: plan`）
3. 在 `clarifications.jsonl` 中记录跟进任务 ID

### Ac3. 记录处置
写入 `task.json` 的 `meta.disposition`：

```json
{
  "outcome": "projected|not_reusable|task_only",
  "reason": "<处置理由>",
  "at": "<时间戳>"
}
```

### Ac4. 架构改进
如结论涉及需要改进的代码架构：
- 提取改进项
- 创建新任务或更新现有任务 backlog

### Ac5. 跨会话桥接（Handoff）
加载 `$PDCA_HOME/skills/handoff-work/SKILL.md`；manual `handoff` 仅保留为用户入口。

### Ac6. 追加日志
加载 `$PDCA_HOME/skills/write-journal/SKILL.md`，追加任务摘要到 `$PDCA_HOME/pdca/journal/YYYY-MM-DD.md`。

### Ac7. 提交（含 disposition）
检查 `$PDCA_HOME/records/<record-id>/evidence/manifest.jsonl` 是否存在。若不存在则提示"请先加载 register-evidence 登记证据再提交"（可跳过：确认无产物需登记时手动确认）。

```bash
git add -A && git commit -m "task <id>: 完成并归档"
```

### Ac8. 归档
1. 加载 `$PDCA_HOME/skills/advance-phase/SKILL.md`，目标 phase: `archive`（校验 disposition → 设置 phase=archive + active=false）
2. 再次提交 metadata 变更：
```bash
git add -A && git commit -m "task <id>: 归档 metadata"
```
3. 将任务目录移到 `archive/`：
```bash
mv pdca/tasks/<MMDD-slug> pdca/tasks/archive/$(date +%Y-%m)/
```

## 退出
- 完成: 任务已归档
- 下一周期: 创建新任务，进入 Plan
