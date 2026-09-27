---
name: pdca-model
description: 用户明确选择本体建模场景，或已有建模任务需要定位场景规则时使用。建模固定 ontology/work 语义；任务结构由 TREE/NODE/DECOMP 后续投影。
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

用户选择具名 modeling task 后，按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的“新建正式任务”顺序固定 TASK/CONTEXT/CAP/CONFIRM，再由 agent-dispatch 原生创建一次。创建成功后新 Agent 只展示自己的 Plan 目标并等待，不把 task creation 当作 Plan 启动。

## 唯一场景语义来源

Model 的对象、阶段义务、跨场景身份与最终交付，统一读取
[SCENE-01 的 pdca-model 章节](../../ontology/process/work-scenarios.md)。

本入口只额外强调三条边界：

- Model 必须形成符合 ONTOLOGY-01 的可定位 ontology object/relation/constraint 与 work instance，不能用设计说明或任务树替代模型；
- Modeling Do/Check 只形成并审查 revision/tree/node candidates；Act 固定 ontology/tree/node 后，DECOMP-01 才能产生正式 child task seed；
- modeling 内部细化与职责变化只按 EVOLVE-01；新的 revision 不自动被其他 task ADOPT，也不因 candidate 存在获得创建权限。

阶段执行时使用 `pdca-plan/do/check/act`。scene Skill 不复制四份阶段方法，也不自动串联 implement/verify。
