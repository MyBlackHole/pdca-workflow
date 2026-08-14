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
