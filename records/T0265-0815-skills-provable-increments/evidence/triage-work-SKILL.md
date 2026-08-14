---
name: triage-work
description: Classify a request, deduplicate it, verify its claim, and create a ready-to-plan task or a documented wontfix outcome.
---

# Triage Work

Move a fuzzy request through: `needs-triage` → `needs-info` → `ready-to-plan` or `wontfix`.

Two categories: `bug` (existing behaviour broken) or `enhancement` (new/improvement).

## Process

### 1. Classify

| Input shape | category | scenario_type |
|-------------|----------|---------------|
| Bug report / defect | `bug` | `bugfix` |
| New feature / module | `enhancement` | `development` |
| "Research / analyse X" | `enhancement` | `research` |
| "Write docs for X" | `enhancement` | `documentation` |
| "Design architecture for X" | `enhancement` | `design` |
| "Review code in X" | `enhancement` | `review` |
| Refactor / optimisation | `enhancement` | `development` |
| Uncertain | keep `needs-triage` | leave blank |

### 2. Deduplicate

Search: `$PDCA_HOME/pdca/tasks/**/task.json` (incl. archive), `$PDCA_HOME/knowledge/out-of-scope/`, `$PDCA_HOME/knowledge/**/*.md`.

### 3. Verify the claim

- **Bug**: reproduce from steps; check git log / code logic
- **Enhancement**: search for existing implementation; check if existing modules can extend

### 4. Grill (if info is insufficient)

Load `$PDCA_HOME/skills/grilling/SKILL.md` to fill gaps. Log Q&A to `clarifications.jsonl` (`source: "triage"`).

### 5. Output

**ready-to-plan**: create the task through the uniform identity entrypoint (repository-level lock + ID reservation + immutable record identity):

```bash
python3 "$PDCA_HOME/scripts/task_identity.py" create \
  --slug <MMDD-slug> \
  --title "<短标题>" \
  --scenario-type <development|bugfix|research|documentation|design|review> \
  --created-at <ISO now>
```

The entrypoint assigns the global unique task ID, derives the immutable `meta.record` (`T<id>-<MMDD>-<slug>`), creates `records/<record>/`, and writes `task.json` / `clarifications.jsonl` / `prd.md` atomically. **Never scan-and-write `task.json` directly** — that race produced historical duplicate IDs.

Then append:
- `prd.md` — skeleton (problem + known info + gaps)
- `triager-brief.md` — 结构化 AGENT-BRIEF，见下方模板与质量约束

### AGENT-BRIEF 模板（triager-brief.md）

```markdown
# Triage Brief — <slug>

- **category**: <bug|enhancement>
- **scenario_type**: <development|bugfix|research|documentation|design|review>
- **summary**: <请求一句话>
- **current behavior**: <现状行为>
- **desired behavior**: <期望行为>
- **key interfaces**: <相关模块/接口概念，不写文件路径>
- **acceptance criteria**: <每条独立可验证，格式"运行 X 得到 Y">
- **out of scope**: <明确排除项>
- **information gaps**: <信息缺口>
- **dedup results**: <查重结果>
- **recommended next steps**: <建议>
```

### AGENT-BRIEF 质量约束（可机器检查）

- **AC 可测性**：每条 acceptance criteria 独立可验证，格式"运行 X 得到 Y"，含可 grep 的可验证信号。
- **durability over precision**：不写 `:line`、具体文件路径或实现结构；写概念级接口与行为，保证 brief 跨改动持久有效。
- **覆盖**：`ready-to-plan` 任务必须产生 `triager-brief.md`，缺 brief 视为 triage 不完整。
- **检查命令**（允许在 Triage 产出后运行验证）：

```bash
# 禁止项：brief 中出现 :line 或文件路径
grep -c ':line\|<file path>' triager-brief.md   # 期望输出 0
# 存在性：brief 含 acceptance criteria 段
grep -c 'acceptance criteria' triager-brief.md   # 期望输出 ≥ 1
```

**wontfix**: write to `$PDCA_HOME/knowledge/out-of-scope/<slug>.md` with the request description, rejection reasons, and date. Close the issue.

## Exit
- `ready-to-plan` → Plan phase
- `wontfix` → archive, no further action
