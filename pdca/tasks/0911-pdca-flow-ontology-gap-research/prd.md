# PDCA 流程本体剩余问题调研

## 目标

以 B（本体建模）视角复核 `ontology:process/pdca-flow-model` 及其关联 PDCA 流程本体，确认是否仍存在结构缺口、关系错误、门禁表达不完整或 AI 工作流适配问题。

## 范围

- `ontology:process/pdca-flow-model`
- `ontology:concept/pdca`、`pdca-phase`、`pdca-transition`、`pdca-gate`
- `ontology/process/flow-plan.md`、`flow-do.md`、`flow-check.md`、`flow-act.md`
- `core_scene`、`skill_route` 与任务/证据/阶段转换的本体关系

## 验收标准

- [ ] AC-1: 输出当前流程本体的节点、关系和不变量审查结果。
- [ ] AC-2: 识别仍存在的问题，按 P0/P1/P2 分级并附可复核证据。
- [ ] AC-3: 明确哪些问题需要优化本体，哪些应留给脚本、skill 或测试层。
- [ ] AC-4: 更新或新建承载问题结论的 ontology，并输出仍需另立 Improvement Task 的实现边界。

## 边界

本任务只做 B 场景的本体复核与问题建模，不实施代码迁移；已有 T2165 继续负责 A/B/C 运行时契约迁移。
