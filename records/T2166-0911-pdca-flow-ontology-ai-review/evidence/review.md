# PDCA 对 AI 工作流的一致性审查

## 结论

当前模型具备 AI 工作流的基本闭环：Plan 提供上下文和验收标准，Do 产生可复核证据，Check 需要用户 verdict，Act 负责知识处置。但仍需改进以下能力：

| 维度 | 判定 | 缺口 |
|---|---|---|
| 上下文 | 部分符合 | 需要统一任务上下文快照和来源优先级 |
| 规划/拆解 | 符合 | 本体树可驱动拆分，但父子 DAG 回写必须有自动测试 |
| 执行器边界 | 符合 | Adapter 与核心 Planner 已分离 |
| 证据链 | 符合 | Evidence、AC、convergence-map 有明确关系 |
| 人工确认 | 符合 | final_confirmation 与 check_confirmation 有硬门禁 |
| 失败恢复 | 部分符合 | rejected receipt 有记录，但恢复策略需统一建模 |
| 可观测性 | 部分符合 | 阶段 receipt 完整，运行效果遥测仍不统一 |

## 后续 Improvement Task 边界

优先级为：P0 统一流程本体模型与 schema 消费关系；P1 补充上下文快照、恢复策略和 DAG 回写测试；P2 增加执行效果遥测与跨轮次指标。每项应独立建立 PRD、证据和 verdict。

Source: `ontology/concept/pdca.md`、`ontology/process/flow-do.md`、`ontology/process/flow-check.md`、`ontology/domain/pdca/skill-advance-phase.md`。
