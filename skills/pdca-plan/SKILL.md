---
name: pdca-plan
description: 用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。
metadata:
  version: 5.0.0-rc.2
---

# Plan：确认问题，建立可验收计划

## 进入 Plan

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。它负责根、项目、原 task/Agent、
Git 追溯、用户回应、撤权与资源的一致性核对；本 Skill 不再复制这些规则。

- 当前会话不是原任务执行者时，只把真实用户操作路由回原 Agent，然后停止本地执行；不可路由就阻断。
- 无正式 task 时返回 `pdca` 定位/创建，不在阶段入口创建替代任务。
- 只有当前用户操作与展示的 Plan 目标匹配时才开始；已有明确有效回应不重复索取。
- 读取[Plan 方法](../../ontology/process/flow-plan.md)与 [SCENE-01](../../ontology/process/work-scenarios.md)
  中当前 `task.scene` 对应章节。scene Skill 只负责场景入口/路由，不再维护第二份阶段方法；其余 authority 按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 按需读取。

Plan 未启动前只沟通问题、范围和目标，不生成正式模型、业务实现或其他 Do 产物。

## 本阶段必须固定

Plan 至少把以下内容变成可验收输入，而不是执行说明的占位符：

- 用户问题、目标、范围/非目标、约束、预期交付；
- 已知事实、假设、unknown 及其来源；
- work product、required actions、AC/oracle、正反验证与失败边界；
- 业务/模型/记录读写域、资源要求和停止条件；
- 每个执行步骤的具体动作、预期结果和验证方式。

需要正式 child 时，按 NODE-01 / DECOMP-01 / CONTEXT-01 检查其固定 ontology 来源、
独立职责、I/O、可独立拒收成果和上下文边界，只形成 seed；是否创建仍由用户工作级操作决定。

只是当前 Do 的局部执行切片时，引用
[CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 定义 Do-only Work Unit；
不要在 Plan 中复制 Contract 字段，也不要把 LOC、工时、token、并行度或 Agent 置信度升级成正式任务依据。

## 完成与停止

保存 plan、固定输入、验收基线和必要 seed，记录 `phase_completed`，报告下一 Do 的固定对象、
写域、资源和限制，然后停止。

Do 的 `phase_start` 必须来自 Plan 完成后的新用户操作；最初“开始”、Plan 内预批准或
future blanket approval 都不能自动启动 Do。重复 Plan 从已固定输入恢复，不重复创建产物。
