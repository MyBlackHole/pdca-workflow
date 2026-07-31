---
schema: pdca.asset/v1
id: R0083-0727-scenario-audit
phase: check
source_ids: [evt-scenario-flow-do, evt-scenario-flow-check, evt-scenario-triage, evt-scenario-flow-plan]
---

## 上下文
评估当前 PDCA 工作流对非软件开发场景的适配性。发现 flow-do 过度耦合到编码路径，无法处理研究、文档、设计、审查等场景。

## 假设与结果
- **假设**：Do 阶段需要场景感知分支才能支持多种工作形态
- **结果**：✅ 确认 — 引入 `meta.scenario_type` + 6 条 Do 执行路径 + Check 场景感知追问

## 分析
修改涉及 4 个文件，+189/-22 行：

| 文件 | 变更 |
|------|------|
| `skills/triage/SKILL.md` | 新增 scenario_type 推断逻辑，triage brief 和 task.json 输出包含该字段 |
| `flows/flow-plan/SKILL.md` | 补充 triage 输出含 scenario_type |
| `flows/flow-do/SKILL.md` | 完全重写为 6 条场景路径（development/bugfix/research/documentation/design/review） |
| `flows/flow-check/SKILL.md` | 回顾和 Grill 阶段按场景分支追问 |

场景覆盖矩阵全部通过：6 种场景各有一条完整的 Do→Check 路径。

## 适用边界
- scenario_type 由 triage 阶段推断，Plan 阶段也可手动修正
- 默认 `development` 确保向后兼容
- "review" 场景不产生代码变更，Check→Act 后可无 commit 归档

## 下一轮建议
用非开发场景（如 research 或 documentation）跑一次端到端验收，确认路径选择正确。