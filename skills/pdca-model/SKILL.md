---
name: pdca-model
description: 用户明确选择本体建模场景，或已有建模任务需要定位场景规则时使用。模型决定正式任务结构与上下文边界。
metadata:
  version: 5.0.0-rc.2
---

# Model：进入本体建模场景

## 场景入口

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。本 Skill 只负责确认/路由
`pdca-model` 场景；四阶段的启动、授权、恢复与停止仍由 phase Skill 和当前 authority 决定。

已有 modeling task 时必须回到原 Agent；当前会话不是执行者时只路由真实用户操作，不接管。
没有 matching task 时，不在本 Skill 内直接开始 Plan/Do。

存在两种合法建模任务来源：

- **已有 ontology-backed node**：固定 node/revision、责任与必要 CONTEXT-01 子图后，由用户显式创建 modeling task；
- **首次 root modeling**：当前 work 尚无 node 时，仅允许 TASK-01 定义的唯一 root modeling bootstrap，
  固定 root goal seed、范围、事实来源和预期模型；尚未形成的 node/revision 保持空，不造占位值。

正式创建按 [agent-dispatch](../../ontology/contracts/agent-dispatch.md)；创建成功后新 Agent 只展示自己的
Plan 目标并等待，不把 task creation 当作 Plan 启动。

## 唯一场景语义来源

Model 的对象、阶段义务、跨场景身份与最终交付，统一读取
[SCENE-01 的 pdca-model 章节](../../ontology/process/work-scenarios.md)。

本入口只额外强调三条边界：

- Model 必须形成可定位的 ontology object/relation/constraint 与 work instance，不能用设计说明或任务树替代模型；
- 正式 child seed 必须由 TREE-01 / NODE-01 / DECOMP-01 从固定模型关系产生，不能从 LOC、文件、token 或并行需求反推；
- modeling Do 的内部细化与职责变化只按 EVOLVE-01 判断；候选新 revision/child 不自动改变其他任务的采用版本或创建权限。

阶段执行时使用 `pdca-plan/do/check/act`。scene Skill 不复制四份阶段方法，也不自动串联 implement/verify。
