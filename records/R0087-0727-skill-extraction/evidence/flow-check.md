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

## 步骤

### 1. 回顾实验
读取 `task.json` 的 `meta.scenario_type`，按场景回顾：

**development / bugfix**：
- `git diff` — 实际变更
- 对比 `prd.md` 验收标准逐条检查

**research / documentation / design / review**：
- 对照 `prd.md` 验收标准和产出物检查
- `evidence/manifest.jsonl` — 证据清单

### 2. Grill
加载 `skills/grill/SKILL.md`，追问结论可靠性。

场景感知的追问：

**development / bugfix**：
- 结论是否有充分证据支持？
- 测试覆盖了关键路径吗？
- 性能/安全方面是否有未暴露的 trade-off？

**research**：
- 调研方法是否充分？
- 是否有遗漏的关键信息来源？
- 结论是否有替代解释？

**documentation / design**：
- 产出物内容是否完整无遗漏？
- 术语与 `pdca/CONTEXT.md` 一致？

**review**：
- 审查是否覆盖了所有关键路径？
- 风险评级是否合理？

追加 Q&A 到 `clarifications.jsonl`（`source: "grill"`）。
模糊术语更新到 `pdca/CONTEXT.md`。

### 3. 验证收敛条件
加载 `skills/verify-convergence/SKILL.md`。

### 4. 结论文档 + 记录判定
加载 `skills/write-conclusion/SKILL.md`。

### 5. 进入 Act 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `act`。
写入 `meta.record` 引用当前结论。

## 退出
- 完成: `meta.phase` = `"act"`
- 注意: rejected/partial 也必须进入 Act，不从 Check 退回 Plan