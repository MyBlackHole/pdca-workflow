---
name: pdca-do
description: 用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。不自动 Check。
metadata:
  version: 5.0.0-rc.2
---

# Do：在原任务里实施获准计划

## 先定位，不以加载当授权

核对本文件经符号链接解析后的真实路径，定位集中 Git 工作副本 **PDCA_ROOT**。
既有任务绑定优先于 cwd 或环境变量；与入口所在根冲突时停止，不在目标项目创建 `.pdca/`
或另一份 records。定位不等于批准业务操作。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读当前绑定项目 context、
自己的 task/原 Agent 绑定、最后完整事件和当前请求。核对记录的
`rules_git_head`/`rules_git_status`；每次获准写入记录前按共同入口重新采集当前 Git 来源。
已有任务不自动改绑或升级规则，原依据缺失或规则冲突时停止；不复制规则、不自动 checkout，
不以新规则改写原授权。

当前会话不是该任务执行者时，只把真实用户操作路由回原 Agent 后停止本地执行；
**不可路由就阻断**。**切换 Skill 不换 Agent**，不要调用新建正式任务来替代原执行者，
不要设置自动 fork 或由父 Agent 接管。加载方法、文件存在和 Plan PASS 都不授权 Do。

开始前核对匹配 task/attempt/phase/run/subject 的**原始用户回应**、固定 Plan 版本、
输入、写域及撤权状态，并核验集中资源预约和实际写权。无任务时返回总入口定位。

## 当前 run

1. 确认 Plan 已 `phase_completed`，且本次 Do `phase_start` 是 Plan 完成后的用户操作；返修使用新的 Do run，不覆盖旧失败证据。
2. 读取[Do 方法](../../ontology/process/flow-do.md)，按 task.scene 读取场景 Skill 的“阶段方法”。
3. 取得并复核[集中预约](../../ontology/concept/resource-ownership.md)，固定实际对象与后端依据；未知结果只对账原 operation，不盲目重试。
4. 在批准范围自主实现、调试和执行必要验证。目标、oracle、写域、资源边界或不可逆动作变化时停止并沟通。
5. 固定本 run 的模型/业务产物、映射、命令/工具原始结果、证据和未验证范围；输出文字不能替代真实产物。

## Do-only Work Unit

Do 内部需要缩小上下文、隔离风险或并行执行时，将执行切成 **Do-only Work Unit**。
Work Unit 不是 PDCA task，不拥有 Plan/Check/Act，也不触发新的阶段授权。

每个 Work Unit 必须使用 [CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 的
`C=(I,O,S,R,T,Φ,Ψ)`：

| 字段 | 含义 |
|---|---|
| I | 固定输入及 ref/digest |
| O | 期望输出与落点 |
| S | 允许读写的作用域 |
| R | 资源、权限和预约 |
| T | 终止/阻断条件 |
| Φ | 完成判据 |
| Ψ | 必须返回的证据与可声明 claim |

Work Unit 的结果至少包含：
`contract_id`、`termination`、`completion`、`outputs`、`evidence`、`claims` 和 `limitations`。
父 Do 只根据这些固定结果继续，不从执行者自述推导额外授权。

### 执行模式

- **inline**：原 Agent 在当前 Do 内直接执行。
- **delegated**：交给隔离上下文执行者，只传 minimum sufficient context、固定 Contract 和共享不变量。
- **external**：交给已获准工具/外部执行机制，以固定结果回传。

这三种模式不绑定具体宿主 API。委派执行者是 Do 的执行单元，不自动成为新的正式 PDCA Agent。
需要正式工作节点时，停止当前扩张，按 [DECOMP-01](../../ontology/concept/task-decomposition.md)
生成候选并等待用户工作级创建操作。

### 协作边界

父 Do **不轮询、不监工、不维护子执行者生命周期**。派发后只消费宿主原生完成事件、
固定结果或用户主动返回的结果；没有事件能力时说明限制，不伪造后台持续运行。
返回状态 unknown 时只对账原请求，不重复派发。

Work Unit 间可以有阻塞边；当前输入 ready 后可在已批准 Do 范围内自主推进。
这不等于可以自动创建正式节点、改变父 Plan 或跨阶段运行。

## 上下文卫生

同一 Work Unit 只读取完成 Contract 所需的局部上下文；不同 Work Unit 不共享活动历史，
只共享固定输入和不变量。新 Do run 从记录恢复，不依赖前一 run 的隐式上下文。
必要压缩只保留 task/attempt/run、固定 Plan、当前 Work Unit Contract、未决 operation 与证据指针。

## 报告与停止

报告实际完成、失败和未验证范围，明确下一 Check 要核对的对象版本及标准。
保存 `phase_completed` 后等待新的 Check `phase_start`；不顺手执行 Check/Act，
不返回父 Agent 代做收尾。

**幂等性：** 同一 run 重放先核对已有 operation/result，不能通过重复委派制造第二份副作用。
