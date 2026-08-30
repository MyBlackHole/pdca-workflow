---
name: flow-plan
description: 计划阶段执行流：triage、逐轮对齐、PRD、任务拆解、知识注入和唯一终审门禁。
---

# PDCA Plan

## 入口

- 新需求、issue 或想法：从 P0 开始。
- 已有 `task.json` 且 `meta.phase=plan`：从 P1 开始。
- 运行 `python3 scripts/pdca_context.py --phase plan` 读取 PDCA 元本体给出的 plan 阶段定义/准入条件/合法后继，作为本阶段执行指引（元本体缺失时回退提示，不阻断流程）。

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

development/bugfix 任务须在此声明其领域本体片段：将构建/复用的本体目录或文件写入 `meta.ontology_fragment`；Do 前置 `ontology-ready` 关卡（`pdca-ontology-ready` 由 PDCA 元本体驱动）会校验其存在且 `pdca.asset/v1` 结构合法。构建 PDCA 元本体自身的自举任务设 `meta.ontology_exempt=true` 以豁免该关卡。

若 `meta.ontology_fragment` 非空（或拆分自带本体片段的父任务），须在 PRD 的 `## 关联本体节点` 小节登记本任务直接消费/产出/对齐的本体节点 id（一行一个 `ontology:...`），供 Do 阶段本体消费回链与可复用知识检索。该小节为可选登记，不影响门禁。

## P2. Grill、建模与方向确认

加载 `$PDCA_HOME/skills/grilling/SKILL.md`，按 round 批量询问当前可答的所有用户决策问题，每问附推荐答案。同步执行 `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`：

- Q&A 追加到 `clarifications.jsonl`（`source: "grilling"`）。
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

## P3.5. 测试接缝确认（development/bugfix 场景）

PRD 的 `## Seam 分析` 章节下填写 `### 声明的测试接缝` 子节，每行一个 seam：

```markdown
### 声明的测试接缝
- seam: <测试文件路径> -> <被测模块路径>
```

向用户展示 seam 清单，请求确认（seam 决定拆解粒度和 Do 阶段测试边界）。修改则继续对齐；确认后进入 P4。research/documentation/design/review 场景无测试产物，跳过本步骤。

## P4. 拆解

大型目标加载 `$PDCA_HOME/skills/to-tickets/SKILL.md`：

- 子 task 的 `parent` 指向父任务；父任务 `children` 列出全部子 ID。
- 子 PRD 包含独立输入、边界和验收标准，粒度不小于一个 PDCA 周期。
- 若 `meta.ontology_fragment` 非空且 PRD 含 `## 拆分映射`，可在 `to-tickets` 启用**关系树驱动拆分**（见该技能步骤）：本体 `composed_of` 树决定子任务边界，`ontology_node_type` 与依赖边自动推导。
- P4 只创建任务，不执行；P6 前禁止调度。

## P5. 知识注入

搜索 `$PDCA_HOME/knowledge/`，只选择影响当前决策的资产，并逐行追加到 `implement.jsonl`：文件、理由、动作和时间。不得为凑数加载全部历史记录。

## P6. 方案终审（唯一签审）

展示完整目标、范围、验收标准、设计与备选取舍、任务树。遗漏回 P2，范围变化回 P1/P2。用户明确批准完整方案后追加。
用户在确认时给出的自由文本反馈（修改要求、深度诉求等原话）须以 `user_meta_feedback`（`captured: true`）落盘后再继续：

```jsonl
{"source":"final_confirmation","summary":"<终审摘要>","response":"confirmed","at":"<ISO 时间>"}
```

优先使用 `python3 "$PDCA_HOME/scripts/append-confirmation.py" --task-dir <task-dir> --source final_confirmation --response confirmed --summary "<终审摘要>"` 自动生成真实 `at`，禁止手写时间戳。

只有该记录且 `response=confirmed` 才能进入 Do；方向确认或子执行器确认均不能替代。`plan -> do` 门禁校验 PRD 的 `## 验收标准` 段必须为 `- [ ] AC-x: ...` checkbox 格式，`### AC-x` 标题式会被拒绝。

development/bugfix 场景额外校验：PRD 含 `### 声明的测试接缝` 子节（缺失即拒绝），并按 `$PDCA_HOME/scripts/seam_contract.py` 校验 seam 声明与实际测试一致。

## P7. 推进

加载 `$PDCA_HOME/skills/advance-phase/SKILL.md`，执行 `plan -> do`。完成态为 `meta.phase=do`。转换前向 `dialogue-log.md` 追加本阶段对话摘要（格式见 handoff-work）。

## 执行器边界

P6 后才可使用抽象能力 `agent.spawn` 调度已确认子任务。用户决策留在主 session，子输出仍需回归 Check。能力不可用时由主 session 顺序执行，不得猜测平台工具。

## 生效自检

- 每个 plan→do 转换的 receipt 存在且 final_confirmation 为 confirmed（可 grep transition-receipts）
- PRD 验收标准全部为 checkbox 格式且每条可在后续产物中判定 ✅/❌
