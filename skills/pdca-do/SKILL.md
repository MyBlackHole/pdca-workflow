---
name: pdca-do
description: 用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。不自动 Check。
metadata:
  version: 5.0.0-rc.3
---

# Do：执行已批准计划

## 进入 Do

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。它只定位根、原 task/Agent、Git 来源、
待决对象与未决 control/resource/dependency refs；具体授权、资源和依赖判断分别交给当前 authority，本 Skill 不重复定义。

- 当前会话不是原任务执行者时，只路由真实用户操作回原 Agent；不可路由就阻断。
- 按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的 phase_start 链核验 Plan predecessor、当前授权与写域，并写入 `phase_started(do)` 后才进入业务方法。
- 返修使用新的 Do run；是否仍可留在原 attempt 由 REWORK-01 + GATE-01 判断，已有 operation/result 先对账。
- 读取[Do 方法](../../ontology/process/flow-do.md)与 [SCENE-01](../../ontology/process/work-scenarios.md) 当前 scene 章节。

## 本阶段动作

在冻结目标、oracle、写域、资源与不可逆副作用边界内自主实现、调试和运行必要验证。
范围、AC/oracle、写域、资源保证或不可逆动作需要变化时，停止受影响动作并回到用户决策，
不能把“实现需要”解释成扩权。

需要局部隔离或并行执行时，按
[CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 使用 Do-only Work Unit。
Contract 的字段、结果结构、上下文隔离、unknown 对账和“不轮询/不监工”语义都只以 CONTRACT-01 为准；
本 Skill 不再复制第二份 Work Unit 规范。

Work Unit 发现新的独立 ontology responsibility 时停止越界部分，把证据交回原 task，并先形成 EVOLVE/TREE/NODE candidate；只有 Modeling Check/Act 固定成 formal node 后，DECOMP-01 才能形成 task seed candidate。不要在 Do 内自动创建正式 task、切换 scene 或改变父 Plan。

## 完成与停止

固定本 run 的真实产物、mapping/模型版本、工具结果、证据、失败与未验证范围后，
按 LOAD-MAP 的 phase completion 链写 `phase_completed(do)` 并投影 awaiting_confirmation。
报告下一 Check 候选对象后停止；Do 不顺手执行 Check/Act。
