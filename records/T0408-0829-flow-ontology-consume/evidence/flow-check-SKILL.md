---
name: flow-check
description: |
  检查阶段执行流。从执行结果到结论的对比分析。
  覆盖假设验证、Grill、结论记录、Verdict 封存。
---

# 检查阶段执行流（PDCA — Check）

## 入口条件
- `task.json` 的 `meta.phase` 为 `check`
- `prd.md` 存在（用于对照验证假设）

## 步骤总览

| 步骤 | 内容 |
|------|------|
| Ch1 | 回顾实验 — 对照 PRD 检查 |
| Ch2 | Grill — 追问结论可靠性 |
| Ch3 | 验证收敛条件 |
| Ch4 | 结论文档 + 记录判定 |
| Ch5 | 结论文档确认（用户 verdict） |
| Ch6 | 进入 Act 阶段 |

## 步骤

### Ch1. 回顾实验
读取 `task.json` 的 `meta.scenario_type`，按场景回顾：

**development / bugfix**：
- `git diff` — 实际变更
- 对比 `prd.md` 验收标准逐条检查
- 若 `meta.ontology_fragment` 存在：确认 `python3 scripts/ontology-validate.py` 通过，且本体新增/修改节点已在 `evidence/manifest.jsonl` 登记

**research / documentation / design / review**：
- 对照 `prd.md` 验收标准和产出物检查
- `evidence/manifest.jsonl` — 证据清单

### Ch2. Grill
加载 `$PDCA_HOME/skills/grilling/SKILL.md`，按 round 批量追问所有当前可答的结论可靠性问题。

场景感知的追问：

**development / bugfix**：
- 结论是否有充分证据支持？
- 测试覆盖了关键路径吗？
- 性能/安全方面是否有未暴露的 trade-off？
- 结论是否可被既有 ontology 节点 / `relations` 支撑？（无本体锚点时显式标注"未关联"）

**research**：
- 调研方法是否充分？
- 是否有遗漏的关键信息来源？
- 结论是否有替代解释？

**documentation / design**：
- 产出物内容是否完整无遗漏？
- 术语与 `$PDCA_HOME/pdca/CONTEXT.md` 一致？

**review**：
- 审查是否覆盖了所有关键路径？
- 风险评级是否合理？

追加 Q&A 到 `clarifications.jsonl`（`source: "grilling"`）。
模糊术语更新到 `$PDCA_HOME/pdca/CONTEXT.md`。

### Ch3. 验证收敛条件
加载 `$PDCA_HOME/skills/verify-convergence/SKILL.md`。

### Ch4. 结论文档 + 记录判定
加载 `$PDCA_HOME/skills/write-conclusion/SKILL.md`。

### Ch5. 结论文档确认
向用户展示结论摘要，获取 verdict 判定：
- **confirmed**：结论成立，进入 Act 完成知识沉淀和归档
- **rejected**：结论不成立，仍进入 Act 进行失败处置（提取教训，不沉淀知识）
- **partial**：结论部分成立，进入 Act 提取有效部分并创建跟进任务

判定后追加记录到 `clarifications.jsonl`（`source: "check_confirmation"`）。用户确认时给出的自由文本反馈（修改诉求、深度评价等原话）须以 `user_meta_feedback`（`captured: true`）落盘，不得只口头响应。

结论不成立（rejected/partial）也必须进入 Act，不从 Check 退回 Plan——Act 阶段会根据 verdict 分支处理。

### Ch6. 进入 Act 阶段
转换前向任务目录 `dialogue-log.md` 追加 Check 阶段对话摘要（格式见 handoff-work）。
加载 `$PDCA_HOME/skills/advance-phase/SKILL.md`，目标 phase: `act`。
写入 `meta.record` 引用当前结论。

## 退出
- 完成: `meta.phase` = `"act"`
- 注意: rejected/partial 也必须进入 Act，不从 Check 退回 Plan
## 生效自检

- conclusion 的每个 AC 判定行可 grep 到证据 ID（`- **AC-x** ✅/❌`）
- 用户 verdict 均有 check_confirmation 留痕且时间线晚于 conclusion 写入
