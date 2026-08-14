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
