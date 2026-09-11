---
schema: pdca.asset/v1
id: ontology:domain/skill-triage-work
name: triage-work
summary: Triage incoming tasks and prioritize based on impact and urgency.
description: Classify a request, deduplicate it, verify its claim, and create a ready-to-plan task or a documented wontfix outcome.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/skill-triage-work/1.0.2
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/triage
    - ontology:concept/domain-modeling
  testable_signal: "运行 grep -q 'Triage Work' ontology/domain/pdca/skill-triage-work.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


--
name: triage-work
description: Classify a request, deduplicate it, verify its claim, and create a ready-to-plan task or a documented wontfix outcome.
---

# Triage Work

Move a fuzzy request through: `needs-triage` → `needs-info` → `ready-to-plan` or `wontfix`.

Two categories: `bug` (existing behaviour broken) or `enhancement` (new/improvement).

## Process

### 1. Classify

| Input shape | category | ontology_role | execution_contract focus |
|-------------|----------|---------------|--------------------------|
| 建立或修订概念、关系、约束 | `enhancement` | `ontology_modeling` | 知识或本体产物、来源动作、范围约束、可验证信号 |
| 将已确认本体投射为代码、文档或配置 | `bug` / `enhancement` | `ontology_projection` | 投射产物、实现/修复动作、测试约束、行为信号 |
| 核验本体与实现、证据或结论的一致性 | `bug` / `enhancement` | `ontology_conformance_verification` | 审查产物、逐项核验动作、独立性约束、符合性信号 |
| Uncertain | keep `needs-triage` | leave blank | leave blank |

`bug` 和 `enhancement` 只描述请求性质，不决定专业职责或执行路径。调研、TDD、诊断、文档写作、`design-it-twice` 和 `code-review` 都是可选动作或工具名称；根据目标把它们写入 `execution_contract.required_actions`，不得据此创建另一套任务类别。

### 2. Deduplicate

Search: `$PDCA_HOME/pdca/tasks/**/task.json` (incl. archive), `$PDCA_HOME/ontology/domain/out-of-scope-*.md`, `$PDCA_HOME/ontology/domain/**/*.md`.

对 out-of-scope 知识库做**概念级 dedup 前置检查**：

```bash
python3 "$PDCA_HOME/scripts/out-of-scope-manager.py" check --concept <concept>
# 命中 → 列出相关概念文件，进入 surfacing（见 wontfix 分支）
python3 "$PDCA_HOME/scripts/out-of-scope-manager.py" list
```

按**概念相似度**匹配（非关键词）："night theme" 命中 `out-of-scope-dark-mode.md`。
命中后 surfacing 给用户："类似 `<file>` 之前拒绝过，因为 `<reason>`，仍要推进？"

### 3. Verify the claim

- **Bug**: reproduce from steps; check git log / code logic
- **Enhancement**: search for existing implementation; check if existing modules can extend

### 4. Grill (if info is insufficient)

Load `ontology:domain/skill-grilling` to fill gaps. Log Q&A to `clarifications.jsonl` (`source: "triage"`).

### 5. Output

**ready-to-plan**: create the task through the uniform identity entrypoint (repository-level lock + ID reservation + immutable record identity):

```bash
python3 "$PDCA_HOME/scripts/task_identity.py" create \
  --slug <MMDD-slug> \
  --title "<短标题>" \
  --ontology-role <ontology_modeling|ontology_projection|ontology_conformance_verification> \
  --created-at <ISO now>
```

创建后必须补齐 `meta.execution_contract` 的 `work_product`、`required_actions`、`constraints` 和 `testable_signal`；缺一项即保持 `needs-info`，不得进入 Plan 终审。

The entrypoint assigns the global unique task ID, derives the immutable `meta.record` (`T<id>-<MMDD>-<slug>`), creates `records/<record>/`, and writes `task.json` / `clarifications.jsonl` / `prd.md` atomically. **Never scan-and-write `task.json` directly** — that race produced historical duplicate IDs.

Then append:
- `prd.md` — skeleton (problem + known info + gaps)
- `triager-brief.md` — 结构化 AGENT-BRIEF，见下方模板与质量约束

### AGENT-BRIEF 模板（triager-brief.md）

```markdown
# Triage Brief — <slug>

- **category**: <bug|enhancement>
- **ontology_role**: <ontology_modeling|ontology_projection|ontology_conformance_verification>；**execution_contract**: <work_product + required_actions + constraints + testable_signal>
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

**wontfix**: 按概念聚合写入 `$PDCA_HOME/ontology/domain/out-of-scope-<concept>.md`：

1. **仅 enhancement**（非 bug）被拒绝时写入；reason 必须 **durable**（避免"现在太忙"这类临时理由——那是 deferral 非拒绝）。
2. **反污染**：因**已实现**而拒绝的请求**禁止**写入 out-of-scope（会污染 dedup 造成假拒绝）——关闭评论指向功能已存在位置：

```bash
python3 "$PDCA_HOME/scripts/out-of-scope-manager.py" add \
  --concept <kebab-case-concept> \
  --reason "<durable reason>" \
  --request "<issue/PR 描述>" \
  [--implemented]   # 已实现时传此标志，脚本拒绝写入
```

3. **概念级聚合**：一个概念一个文件；同一概念的后续请求**追加**到已有文件的 `## Prior requests`（文件数不变），不同概念才新建文件。
4. 关闭 issue 时在评论中提及 `ontology/domain/out-of-scope-<concept>.md`。

## Exit
- `ready-to-plan` → Plan phase
- `wontfix` → archive, no further action

## 已知坑

- 曾经只写 `<slug>.md` 不做概念级聚合，导致同一概念重复文件、dedup 失效——务必聚合到 `ontology/domain/out-of-scope-<concept>.md`（T0266）。
- "已实现"的拒绝禁止写入 out-of-scope：会污染 dedup 造成假拒绝；关闭评论应指向功能已存在位置（T0266）。
