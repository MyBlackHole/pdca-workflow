---
name: pdca-do
description: 用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。不自动 Check。
metadata:
  version: 5.0.0-rc.2
---

# Do：执行已批准计划

## 进入 Do

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。根、原 task/Agent、Git 依据、
用户回应、撤权与资源核对都以该入口为准，本 Skill 不重复定义。

- 当前会话不是原任务执行者时，只路由真实用户操作回原 Agent；不可路由就阻断。
- 必须存在已完成且仍匹配当前对象的 Plan，并有 Plan 完成后的真实 Do `phase_start`。
- 返修使用新的 Do run；已有 operation/result 先对账，不通过重放制造第二份副作用。
- 读取[Do 方法](../../ontology/process/flow-do.md)和当前 scene Skill 的“阶段方法”；
  其他 authority 仅按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的事件需要读取。

## 本阶段动作

在冻结目标、oracle、写域、资源与不可逆副作用边界内自主实现、调试和运行必要验证。
范围、AC/oracle、写域、资源保证或不可逆动作需要变化时，停止受影响动作并回到用户决策，
不能把“实现需要”解释成扩权。

需要局部隔离或并行执行时，按
[CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 使用 Do-only Work Unit。
Contract 的字段、结果结构、上下文隔离、unknown 对账和“不轮询/不监工”语义都只以 CONTRACT-01 为准；
本 Skill 不再复制第二份 Work Unit 规范。

Work Unit 发现新的独立 ontology responsibility 时停止越界部分，按 DECOMP-01 形成候选证据；
不要在 Do 内自动创建正式 task、切换 scene 或改变父 Plan。

## 完成与停止

固定本 run 的真实产物、mapping/模型版本、命令或工具结果、证据、失败与未验证范围，
保存 `phase_completed`，报告下一 Check 应核验的对象版本和标准，然后停止。

Check 必须由新的用户操作启动；Do 不顺手执行 Check/Act，也不让父 Agent 代做收尾。
