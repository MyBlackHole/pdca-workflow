---
name: pdca-implement
description: 用户明确选择本体投影场景，或已有投影任务需要定位场景规则时使用。只实现固定本体节点，不重新定义模型。
metadata:
  version: 5.0.0-rc.2
---

# Implement：进入本体投影场景

## 场景入口

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。本 Skill 只负责确认/路由
`pdca-implement` 场景，不承担 phase 的授权或执行。

已有 implement task 时回原 Agent；当前会话不是执行者时只路由真实用户操作，不接管。
没有 matching task 时，只能基于已固定的 node/revision、CONTEXT-01 子图、目标写域和 mapping
提出具名 task creation 所需输入，由用户显式创建；不能直接开始实现。

## 唯一场景语义来源

Implement 的对象、阶段义务、mapping、跨场景身份与验收，统一读取
[SCENE-01 的 pdca-implement 章节](../../ontology/process/work-scenarios.md#pdca-implement把模型投影成真实实体)。

本入口只额外强调：

- implementation 必须绑定固定 `work_id/node_id`、ontology revision、responsibility/I/O/constraints 和 mapping；
- 模型缺失/错误时停止依赖该模型的写入，按 EVOLVE-01 报告证据与修订建议，不在 implement 中顺手改模型；
- Do 内的局部执行只按 CONTRACT-01 使用 Work Unit；Work Unit 不创建 node/task，不拥有新的 ontology responsibility；
- 兄弟/child 的活动历史不是当前 task 输入，组合只消费固定 deliverable/interface。

阶段执行时使用 `pdca-plan/do/check/act`。scene Skill 不复制四阶段方法，也不自动启动 verify。
