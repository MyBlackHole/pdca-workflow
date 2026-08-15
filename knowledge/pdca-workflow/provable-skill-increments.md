# 可证明 Skill 增量方法：AGENT-BRIEF / Wide-Refactor / Ticket Claim

> 来源：T0265（0815-skills-provable-increments）。本知识沉淀从 mattpocock/skills 借鉴并本地化的三个可证明增量机制，供后续任务复用。

## 背景

对 mattpocock/skills 重新评估后确认三个可被硬指标证明价值的机制在本仓库缺失。本知识记录三个机制的落地形态与可证明指标，作为后续扩展的参考。

## 机制一：AGENT-BRIEF 结构化模板（triage-work）

**目的**：让 triage 产出可直接进入 Do 的高质量 brief，且质量可机器检查。

**模板字段**（`triager-brief.md`）：

```
category / scenario_type / summary / current behavior / desired behavior /
key interfaces / acceptance criteria / out of scope / information gaps /
dedup results / recommended next steps
```

**可检查质量约束**：
- AC 可测性：每条 AC 格式"运行 X 得到 Y"，含可 grep 的可验证信号。
- durability over precision：不写 `:line`、具体文件路径或实现结构，写概念级接口与行为。
- ready-to-plan 任务必须产生 `triager-brief.md`。

**检查命令**：
```bash
grep -c ':line\|<file path>' triager-brief.md   # 期望 0
grep -c 'acceptance criteria' triager-brief.md   # 期望 ≥ 1
```

**可证明指标**：brief 覆盖率为 100%、AC 存在性、禁止项为 0。

## 机制二：Wide-Refactor 保绿序列化（to-tickets）

**目的**：blast radius 横跨全库的重构（全局改名/改类型/改接口签名）禁止单提交打穿，逐批保持 CI 绿。

**序列**：expand → 分批迁移 → contract → (integrate-and-verify)

1. **expand**：新旧形式并存，保留旧形式；旧形式仍被契约测试覆盖。
2. **分批迁移**：按 blast radius 分批，每批 `blocked by expand`，每批迁移后跑完整测试保持 CI 绿。
3. **contract**：无调用者后删除旧形式，`blocked by` 全部迁移批。
4. **批次内无法保绿**：共享集成分支 + 末尾 integrate-and-verify 票。

**可证明指标**：逐批 CI 绿比例 = 100%、expand 阶段旧形式契约测试存在、单批迁移调用点数可审计。

> 注意：0809 任务曾将 expand-contract 列为不落地；T0265 重新决策落地，理由是逐批 CI 绿比例硬指标可证明重构安全性。

## 机制三：Ticket Claim 并发防冲突（wayfinding-work）

**目的**：并发 session 不会重复处理同一张决策票。

**流程**：选票后立即 claim（写 `claimed-by: <session-id>` + `in-progress`）→ 只有 `open + unblocked + unclaimed` 票可选 → 并发 session 跳过已认领票 → 完成后 resolve 清除。

**实现**：`scripts/check-ticket-claims.py` claim/resolve/status 状态机，状态写 `tickets/claims.jsonl`（每行一个事件，可重放）。

```bash
python3 scripts/check-ticket-claims.py claim   --ticket TK-1 --by sess-a
python3 scripts/check-ticket-claims.py resolve --ticket TK-1 --by sess-a
```

**状态机规则**：
- 重复 claim → `ALREADY_CLAIMED`（退出码 1）。
- 非认领者 resolve → `NOT_CLAIMANT`（退出码 1）。
- resolve 后清除 claim，可被再认领。

**可证明指标**：冲突率可统计（被拒的并发 claim 次数）；claim → resolve 单票完成时间可归因到 session。

## 通用原则

- **可证明优先**：每个机制落地时必须配硬指标与测试断言（结构契约 + 行为状态机），指标优先于直觉。
- **文档增量 + 测试接缝**：skill 增量为 markdown 文档，测试用 grep/正则断言结构契约；行为机制用子进程状态机测试。
- **失败驱动实现**：先写失败测试（红），再实现（绿），保证测试真实覆盖。
- **推翻旧决策需记录**：推翻历史结论（如 0809 不落地 expand-contract）须在 PRD 与 conclusion 中记录理由。

## 后续候选

- AGENT-BRIEF 质量约束接入自动门禁（triage 产出时拦截）。
- claim 状态机进程级文件锁（消除极端并发竞态）。
- wide-refactor 逐批 CI 绿脚本化（记录每批提交 → 校验每批测试 → 输出绿比例）。

## 第二轮：行为级可证明增量（T0266）

> 来源：T0266（0815-skills-round3）。三个增量全部为**行为级**硬指标（真实状态机 fixture / 确定性决策表），比 T0265 的文档结构契约更硬。

### 机制四：out-of-scope 概念聚合知识库（triage-work）

**目的**：被拒绝特性请求的概念级聚合，供 triage dedup surfacing 历史拒绝理由。

- **一个概念一个文件**：`knowledge/out-of-scope/<concept>.md`（kebab-case）。
- **同概念追加**：第二次拒绝追加到已有文件 `## Prior requests`（文件数不变）；不同概念才新建。
- **反污染**：因"已实现"而拒绝的请求**禁止**写入（会污染 dedup 造成假拒绝），脚本 `--implemented` 标志直接拒绝。
- **dedup 前置检查**：triage 时按概念相似度匹配（非关键词），命中则 surfacing 给用户。
- **写入条件**：仅 enhancement（非 bug）被 wontfix 拒绝时写入；reason 必须 durable（"现在太忙"是 deferral 非拒绝）。

**实现**：`scripts/out-of-scope-manager.py` add/check/list。

**可证明硬指标**：聚合状态机（同概念文件数不变/不同概念新建）；反污染（--implemented 拒绝写入）；check surfacing 历史理由——全部脚本可断言。

### 机制五：merge-conflicts intent-based 解析

**目的**：从策略表（ours/theirs/manual）升级为按意图解析，保留双方真实意图。

- **找 primary source**：读 commit/PR/issue 理解每侧原始意图。
- **保留双方意图**：可兼得则兼得；不兼容选符合 merge 目标的并记录权衡。
- **绝不 --abort**：merge 冲突是状态不是错误。
- **跑自动化检查**：typecheck → tests → format，修复 merge 破坏。

**可证明硬指标**：真实 git fixture 断言——解析完成不 abort、`git diff --check` 无残留标记、双方意图均保留。

### 机制六：DEEPENING 深化测试策略（design-it-twice）

**目的**：安全深化浅模块集群的确定性决策表。

| 依赖类别 | 测试策略 | adapter |
|---|---|---|
| in-process | 合并模块，直接经新接口测试 | 否 |
| local-substitutable | 本地替身测；内部接缝，外部接口无 port | 否 |
| remote-owned | 接缝定义 port，注入 adapter；测试用内存 adapter | 是 |
| true-external | 注入为 port；测试提供 mock adapter | 是 |

- **seam 纪律**：one adapter = 假设性接缝；two adapters = 真实接缝。
- **deletion test**：删掉模块复杂度消失 = pass-through 不挣存在；散布到 N 调用点 = 挣存在。
- **replace, don't layer**：深化接口测试存在后删除浅模块旧单测；接口就是测试面；测试挺过内部重构。

**可证明硬指标**：依赖分类→测试策略的确定性映射可脚本断言（4 类互异）。

## 方法论演进（T0265 → T0266）

| 维度 | T0265（文档结构级） | T0266（行为级） |
|---|---|---|
| 指标类型 | grep 结构契约（文档含某字段） | 状态机行为 + 真实 git fixture + 确定性决策表 |
| 测试载体 | 读文件断言 marker | 临时目录状态机、真实 git merge 冲突、决策表映射 |
| 强度 | 可接受（文档存在性） | 更硬（行为可观察、可复现） |
| 共同点 | 失败驱动实现、可证明优先、seam 契约 | 同左 |

## 第三轮：skill 结构契约 + Gotchas 段机制（T0267）

### 机制七：skill 结构契约检查器（scripts/check-skill-structure.py）

Anthropic skill authoring best practices + agentskills.io 规范（pedronauck
validate-metadata.py 同源）脚本化，对 `skills/*/SKILL.md` 全量断言：

- **硬错误**（exit-code 1）：name 格式/长度（`^[a-z0-9]+(-[a-z0-9]+)*$`、1-64）、description 长度（<=1024）、XML 指令标记、SKILL.md <=500 行、Windows 路径（盘符正则 `[A-Za-z]:[\\/]`）、gotchas 段缺失/过短。
- **软警告**（报告不阻塞，`--exit-code` 计入）：description 第一/二人称、缺触发词、无显式完成准则（completion criterion 启发式）。

**可证明硬指标**：违规 fixture 逐项报告并 rc=1；全量 39 正式 skills error_count=0；
`--json` 结构化输出供断言。

### 机制八：Gotchas 段机制（全量强制 + 核心溯源）

Anthropic 内部经验"Gotchas 是 skill 最高信号内容"——从真实失败点积累：

- 每个 skill 含非空 `## 已知坑`/`## Gotchas` 段（双语段名检查器都认）。
- 核心 9 个 skill 的 gotchas 从历史任务真实失败点提取，含记录级来源引用：
  - convergence 文本须与 task.json 逐字一致（CONVERGENCE_TEXT_MISMATCH）
  - `git merge` 冲突返回码 1 是正常状态需 `git_allow_failure`
  - 改 skill 后 SKILLS-INDEX.md 过期需重新生成
  - register-evidence `--file` 须唯一文件名
  - check_confirmation 须带 response 字段
- 抽检：正则提取 T0xxx 记录 id，records/ 前缀匹配或归档 task.json id 匹配。

**可证明硬指标**：段存在性 + 核心 9 来源 token 在段内 + 引用目标目录存在。

## 方法论演进（T0265 → T0267）

| 维度 | T0265（文档结构级） | T0266（行为级） | T0267（skill 结构契约层） |
|---|---|---|---|
| 指标类型 | 单 skill 文档 grep 契约 | 状态机/git fixture/决策表 | 全量 39 skills 机器可判定契约 + gotchas 段溯源 |
| 测试载体 | 读单文件断言 marker | 临时目录/真实 git | 全量扫描 + 违规 fixture + subprocess CLI |
| 覆盖广度 | 单 skill | 单 skill 行为 | 全量 skill 仓库质量底线 |
| 强度 | 可接受 | 更硬（行为） | 硬（机器可判定）+ 溯源（真实性） |
| 来源 | mattpocock | mattpocock | Anthropic 官方/内部 + pedronauck + agentskills.io |

## 第四轮：AGENT-BRIEF 真实效果审计 + 采用度结构化（T0268）

### 机制九：采用度结构化（scripts/check-triage-brief.py）

把"机制是否被用"变成可量化复现的指标：

- 契约解析：triager-brief.md 6 字段宽松匹配（category/evidence/dedup/scenario/priority/actionable），兼容中英文早期格式。
- 历史全量回溯：扫描 pdca/tasks 全量（含归档）93 个 brief，核心三字段全含 58.1%。
- 基线固化：采用率写入测试（>= 下限防回归），后续轮次可对比演进。

### 审计结论：AGENT-BRIEF effectiveness verdict = partial

按 real-usage-effectiveness-audit 三层口径：

- **实现正确性** ✓：契约测试全绿。
- **运行数据可用性** ✓：93 brief 可重建；T0265 落地后 round62/66/67 核心字段 100%。
- **效果闭环** ✗：无 decision→candidate→Improvement Task→effectiveness verdict 反馈链。

**提升作用判定**：AGENT-BRIEF 的"结构化采用"维度成立（supported，有真实采用 + brief→design→evidence 转化证据）；"效果验证"维度未闭环（partial）。四轮增量均属"实现正确 + 运行可用"层，缺第三层。

### 审计方法论教训

- **前置误判**：初版"机制采用率=0"是 grep 关键词误判（产出文件名 triager-brief.md ≠ 机制名 AGENT-BRIEF）。审计须按产出物实际命名/形态判定，不能按机制名 grep。
- **三层证据不可互相替代**：fixture 全绿与真实采用可以同时一真一假；运行可用与效果闭环也可同时一真一假（T0260/T0268 实例）。

## 方法论演进（T0265 → T0268）

| 维度 | T0265-T0267（实现/结构/行为契约） | T0268（效果审计层） |
|---|---|---|
| 证明对象 | 机制存在且符合契约 | 机制是否被真实采用 + 是否有提升作用 |
| 方法 | 测试/脚本断言 | 历史全量回溯 + 三层证据 + 四轴评分 + verdict |
| 结论形态 | supported（可证明落地） | partial（有采用、无闭环） |
| 价值 | 质量底线 | 确定性（区分"实现正确"与"效果有效"） |

## 第五轮：AGENT-BRIEF 决策兑现回读闭环（T0269）

### 机制十：决策兑现回读（scripts/recall-brief-decisions.py）

把"机制决策是否真正落地"变成可复现的回读矩阵：

- 决策提取：triager-brief.md 的推荐方向/已验证问题/信息缺口/风险章节 → 结构化决策（类型 + 文本）。
- 命中检测：决策关键词在任务产出（design/research/implement/do-evidence/conclusion）计数，生成矩阵骨架。
- 兑现状态：审计在矩阵标注 fulfilled/partial/not-fulfilled/unknown + 依据引用（产出文件行）。
- 兑现率：从矩阵解析（fulfilled+partial 计入，unknown/未标注不计入，除零保护）。

### 回读结论：决策兑现率 100%（21/21），直接兑现 90.5%（19/21）

- round62（T0248）9/9 兑现到 do-evidence；round66（T0252）3/3 风险全覆盖进 design；round67（T0253）7 兑现 + 2 partial。
- not-fulfilled = 0：无 brief 决策被实施推翻。
- 2 项 partial 根因 = 信息缺口未量化（旋转盘测量遗漏、重复发送窗口/重做量未定数值），非机制失效。

### AGENT-BRIEF effectiveness verdict 更新（partial → partial-progressed）

- 决策兑现维度：**supported**（21/21 进产出）。
- 效果验证维度：**pending**（样本任务进行中，结果验证环待完成）。

### 审计方法论教训（回读口径）

- **兑现判定口径**：样本进行中无最终 verdict 时，兑现 = 决策进入实施产出（design/evidence 引用），结果验证单独标注待完成；不可混同"决策兑现"与"预测准确"。
- **命中检测陷阱**：glob 不能用正则语法（`do-evidence.*\.md` 匹配不到文件）；停用词过滤是命中质量的先决条件。
- **矩阵即契约**：状态枚举合法 + 依据引用 + 兑现率解析，使回读结论可复现、可断言。

## 方法论演进（T0265 → T0269）

| 维度 | T0265-T0267（实现/结构/行为契约） | T0268（效果审计层） | T0269（决策兑现闭环） |
|---|---|---|---|
| 证明对象 | 机制存在且符合契约 | 机制是否被真实采用 + 是否有提升作用 | 机制决策是否真正进入实施产出 |
| 方法 | 测试/脚本断言 | 历史全量回溯 + 三层证据 + 四轴评分 | 决策回读矩阵 + 兑现率 + 依据引用 |
| 结论形态 | supported（可证明落地） | partial（有采用、无闭环） | partial-progressed（兑现环闭合，验证环 pending） |
| 价值 | 质量底线 | 确定性 | 从"被采用"到"被兑现"的闭环证据 |

## 第六轮：门禁有效性审计 + transition 拒绝留痕（T0270）

### 机制十一：门禁合规扫描（scripts/audit-gate-compliance.py）

把"门禁是否被执行"变成全局可审计指标：

- 全量扫描 154 任务：receipts/verdict/convergence/final_confirmation 覆盖率 + id 唯一性 + 归档一致性。
- 异常分类：legacy_no_gate（机制前任务仅报告）vs gate_incomplete（真违规候选）vs id_collision/archive_dup/active_stale。
- 报告含覆盖率、阶段分布、异常清单、结论。

### 机制十二：transition 拒绝留痕（rejected receipt）

门禁拦截首次可计数：

- 4 拒绝点（NON_ADJACENT/PRD/gate_issues/schema）统一写 `transition-receipts/rejected-<ns>-<to>.json`（schema pdca.gate-rejection/v1）。
- 纳秒时间戳保证多次拒绝不覆盖；成功路径不变。

### 审计结论

- 门禁覆盖率：receipts 81.2%、verdict 79.2%、convergence 95.5%、final_confirmation 84.4% —— 门禁在近 8 成任务完整执行。
- 真违规 6 个（gate_incomplete）：T0207/T0208/T0209 归档但无 verdict（check→act 门禁要素缺失）最高优先。
- id 撞车 25 组 + 重复归档 2 + active 残留 2：T0262 identity 机制上线前的存量缺陷。
- 历史 rejected receipts=0：此前拦截无留痕（第五轮多次被拒均未记录），机制上线后可计数。

### 审计方法论教训

- **门禁有效性需双向证明**：覆盖率（被执行）+ 拒收留痕（拦截被记录）缺一不可；光有覆盖率无法证明拦截真实发生。
- **分类先行**：机制前任务与真违规必须区分，否则审计报告会被历史噪音淹没。
- **变更安全**：给核心脚本（transition-phase）加拒绝留痕时，成功路径必须有对照测试兜底，避免破坏既有语义。

## 方法论演进（T0265 → T0270）

| 维度 | T0265-T0267 | T0268-T0269 | T0270（流程元审计） |
|---|---|---|---|
| 证明对象 | 机制存在且符合契约 / 被采用 / 被兑现 | 机制效果闭环 | **门禁体系本身被完整执行且拦截可审计** |
| 方法 | 测试/回读 | 三层证据/回读矩阵 | 全量合规扫描 + 拒绝留痕 + 异常分类 |
| 结论形态 | supported / partial-progressed | 效果闭环推进 | 门禁有效性确立（覆盖 8 成 + 拦截留痕） |
| 价值 | 质量底线 → 确定性 | 闭环证据 | 流程可信度的元验证 |
