---
name: pdca-plan
description: 用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。
metadata:
  version: 5.0.0-rc.4
---

# Plan：确认问题，建立可验收计划

## 进入 Plan

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。它负责定位根、项目、原 task/Agent、
Git 来源、待决对象及未决 control/resource/dependency refs；具体授权、资源、依赖语义再由对应 authority 判断，本 Skill 不复制这些规则。

- 当前会话不是原任务执行者时，只把真实用户操作路由回原 Agent，然后停止本地执行；不可路由就阻断。
- 共同恢复入口未能定位唯一身份、正式 task/attempt 与原 Agent 时，立即返回 `pdca` 或请求缺少的精确输入并停止；无正式 task 时由 `pdca` 定位/创建，不在阶段入口创建替代任务。此时必须原样使用 entry-recovery 的身份门禁短答模板：只请求精确 `project_id/workspace_id`，仅在用户明确续做既有 task 时请求 `task_id`，并说明未读 `records/`、未开始 phase。不得追加解释、`TARGET_ROOT`/task 名称/记录写权限要求、records 枚举指引、业务细节、产品选项/AC、Plan 预览或执行步骤，也不得读取 Plan/SCENE-01 业务方法或以“准备 Plan”为由提前开始业务分析。
- 对已定位的原 task，按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的 phase_start 链完成 CONFIRM → GATE → TRANSITION → STATE；只有 Gate ready、写入匹配的 `phase_started(plan)` receipt 且 STATE 投影 running 后，才进入业务方法。
- 进入 Plan 后再读取[Plan 方法](../../ontology/process/flow-plan.md)与 [SCENE-01](../../ontology/process/work-scenarios.md) 当前 scene 章节；phase_started/STATE 前不预读业务方法。

## 本阶段必须固定

Plan 至少把以下内容变成可验收输入，而不是执行说明的占位符：

- 用户问题、目标、范围/非目标、约束、预期交付；
- 已知事实、假设、unknown 及其来源；
- work product、required actions、AC/oracle、正反验证与失败边界；
- 业务/模型/记录读写域、资源要求和停止条件；
- 每个执行步骤的具体动作、预期结果和验证方式。

若产物需要保留被审版本，先固定本 task 允许使用的版本命名空间、禁止覆盖范围与资源边界，再列本次 run 的具体输出。例如候选本体的后续修订应能在同一获准 work 范围内保留旧版并另存新版，不能只批准首版文件后才发现没有返工空间。命名空间不扩大到其他 work，也不预批未来 phase；每次 Do 仍对其固定输入、具体产物与写入操作单独授权。

需要正式 child 时，只有目标 child 已经属于 fixed tree/node 且满足 NODE-01，才按 DECOMP-01 形成 task seed candidate，并让 CONTEXT-01 后续选择 assignment refs。Plan 新发现但尚未固定的 responsibility 只能进入 EVOLVE/TREE/NODE candidate，不得提前 seed；是否创建仍由用户工作级操作决定。

只是当前 Do 的局部执行切片时，引用
[CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 定义 Do-only Work Unit；
不要在 Plan 中复制 Contract 字段，也不要把 LOC、工时、token、并行度或 Agent 置信度升级成正式任务依据。

## 完成与停止

固定 plan、输入、验收基线，以及前提已满足时的 task seed candidate 后，按 LOAD-MAP 的 phase completion 链写
`phase_completed(plan)` 并投影 awaiting_confirmation；报告下一 Do 候选对象后停止。
下一阶段授权仍由 CONFIRM-01 单独产生。重复 Plan 从固定输入恢复，不重复创建产物。
