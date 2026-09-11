# PDCA 流程本体建模与 AI 工作流一致性审查

## 目标

先建立 PDCA 流程本体模型，再审查该模型是否适合 AI 工作流执行，形成可实施的模型缺口与改进任务边界。

## 范围

- 建模 `plan → do → check → act → archive` 的阶段、转换、门禁、证据、产物和用户确认关系。
- 建模本体树驱动的 B 本体建模、A 本体实现、C 本体验证及其 skill/tool route。
- 按 AI 工作流要求审查：上下文注入、任务分解、执行器边界、证据链、人工确认、失败恢复、可观测性和持续改进。
- 只产出本体模型、审查报告和后续 Improvement Task 边界，不直接修改生产脚本。

## 验收标准

- [ ] AC-1: 产出完整 PDCA 流程本体模型，明确节点、关系、状态转换和核心不变量。
- [ ] AC-2: 产出 AI 工作流一致性审查，逐项覆盖上下文、规划、执行、检查、确认、恢复和审计。
- [ ] AC-3: 对每个缺口给出证据、优先级、影响范围和后续 Improvement Task 边界。
- [ ] AC-4: 模型与审查报告通过 ontology-validate、图完整性和研究/设计文档门禁。

## 关联本体

- `ontology:concept/pdca`
- `ontology:process/flow-plan`
- `ontology:process/flow-do`
- `ontology:pattern/pdca-core-scene-layering`

## 边界

本任务是建模与审查，不在本任务内实施 T2165 的 A/B/C 运行时迁移，也不直接覆盖权威流程正文。
