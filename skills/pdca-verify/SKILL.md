---
name: pdca-verify
description: 用户明确选择本体符合性验证，或已有验证任务需要定位场景规则时使用。验证同一节点的需求→模型→实现→行为。
metadata:
  version: 5.0.0-rc.2
---

# Verify：进入独立符合性验证场景

## 场景入口

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。本 Skill 只负责确认/路由
`pdca-verify` 场景，不把普通 Check 或一次性第二视角升级成正式 verification。

已有 verify task 时回原 Agent；当前会话不是执行者时只路由真实用户操作，不接管。
没有 matching task 时，只能基于固定 node/revision、implementation/mapping version、需求/AC、
CONTEXT-01 子图和必要行为证据提出具名 verify task 输入，由用户显式创建 fresh Agent。

## 唯一场景语义来源

Verify 的验证链、阶段义务、上下文隔离、finding 与处置，统一读取
[SCENE-01 的 pdca-verify 章节](../../ontology/process/work-scenarios.md#pdca-verify验证实现是否忠实于模型和需求)。

本入口只额外强调：

- Verify 绑定与被审实现相同的语义 node 和明确 revision，不重新建模或重拆任务；
- 实现报告与其他 Agent 结论只是 claim，不能替代固定 implementation、行为观察与反证；
- fresh verify Agent 不继承 implement/父/兄弟完整活动历史；追加调查仍受 CONTEXT-01 的读域/写域区分；
- 审查对象、模型或实现不能由 Verify 修改；模型遗漏按 EVOLVE-01 报告，证据不足保持 unknown/not_run。

阶段执行时使用 `pdca-plan/do/check/act`。scene Skill 不复制四阶段方法。
