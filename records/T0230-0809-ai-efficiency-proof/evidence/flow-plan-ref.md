---
name: flow-plan
description: 计划阶段执行流：triage、逐轮对齐、PRD、任务拆解、知识注入和唯一终审门禁。
---

# PDCA Plan

## 入口

- 新需求、issue 或想法：从 P0 开始。
- 已有 `task.json` 且 `meta.phase=plan`：从 P1 开始。

| 步骤 | 产出 |
|------|------|
| P0 Triage | 分类、查重、claim 验证、task/prd 骨架 |
| P1 澄清 | 问题、目标、验收标准 |
| P2 对齐 | Grill、术语/ADR、方向确认 |
| P3 PRD | 完整规格 |
| P4 拆解 | 独立子任务；不执行 |
| P5 注入 | 最小相关知识列表 |
| P6 终审 | 唯一用户签审门禁 |
| P7 推进 | `plan -> do` |

## P0. Triage

加载 `$PDCA_HOME/skills/triage-work/SKILL.md`；无法加载时按其核心合约执行：

1. 分类为 bug/enhancement 并设置 `scenario_type`。
2. 搜索活跃/归档 task 与 knowledge 查重。
3. 用代码、文档或可执行检查验证 claim；事实不询问用户。
4. 信息不足才进入逐轮 Grill。
5. 创建 `meta.phase=plan` 的 task、PRD 骨架和 triage brief。

## P1. 澄清

读取已有 `prd.md`、`design.md`、`implement.md`，补齐问题陈述、目标和可测验收标准。

## P2. Grill、建模与方向确认

加载 `$PDCA_HOME/skills/grilling/SKILL.md`，按 round 批量询问当前可答的所有用户决策问题，每问附推荐答案。同步执行 `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`：

- Q&A 追加到 `clarifications.jsonl`（`source=grilling`）。
- 模糊术语立即更新 `$PDCA_HOME/pdca/CONTEXT.md`。
- 不可逆、非显然且有权衡的决策写入 `$PDCA_HOME/docs/adr/`。
- 复杂任务（3+ 模块、外部系统或数据变更）补充 `design.md` 和 `implement.md`。

决策树闭合后，向用户展示目标、范围、方案方向、验收标准和关键取舍，请求方向确认。修改则继续 Grill；确认则追加：

```jsonl
{"source":"direction_confirm","summary":"<方向摘要>","response":"confirmed","at":"<ISO 时间>"}
```

方向确认只记录对齐，不是阶段门禁。

## P3. 合成 PRD

按 `$PDCA_HOME/templates/to-spec/SPEC.md` 完成问题、方案、用户故事、实现/测试决策、范围外和备注。所有验收项必须有明确 pass/fail。

## P4. 拆解

大型目标加载 `$PDCA_HOME/skills/to-tickets/SKILL.md`：

- 子 task 的 `parent` 指向父任务；父任务 `children` 列出全部子 ID。
- 子 PRD 包含独立输入、边界和验收标准，粒度不小于一个 PDCA 周期。
- P4 只创建任务，不执行；P6 前禁止调度。

## P5. 知识注入

搜索 `$PDCA_HOME/knowledge/`，只选择影响当前决策的资产，并逐行追加到 `implement.jsonl`：文件、理由、动作和时间。不得为凑数加载全部历史记录。

## P6. 方案终审（唯一签审）

展示完整目标、范围、验收标准、设计与备选取舍、任务树。遗漏回 P2，范围变化回 P1/P2。用户明确批准完整方案后追加：

```jsonl
{"source":"final_confirmation","summary":"<终审摘要>","response":"confirmed","at":"<ISO 时间>"}
```

优先使用 `python3 "$PDCA_HOME/scripts/append-confirmation.py" --task-dir <task-dir> --source final_confirmation --response confirmed --summary "<终审摘要>"` 自动生成真实 `at`，禁止手写时间戳。

只有该记录且 `response=confirmed` 才能进入 Do；方向确认或子执行器确认均不能替代。`plan -> do` 门禁校验 PRD 的 `## 验收标准` 段必须为 `- [ ] AC-x: ...` checkbox 格式，`### AC-x` 标题式会被拒绝。

## P7. 推进

加载 `$PDCA_HOME/skills/advance-phase/SKILL.md`，执行 `plan -> do`。完成态为 `meta.phase=do`。

## 执行器边界

P6 后才可使用抽象能力 `agent.spawn` 调度已确认子任务。用户决策留在主 session，子输出仍需回归 Check。能力不可用时由主 session 顺序执行，不得猜测平台工具。
