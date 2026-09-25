---
name: pdca-plan
description: 用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。
metadata:
  version: 5.0.0-rc.2
---

# Plan：确认问题，建立可验收计划

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
**不可路由就阻断**。**切换 Skill 不换 Agent**，不要调用新建工具、设置自动 fork
或由父 Agent 接管。加载方法、文件存在和上一阶段 PASS 都不授权本阶段。

开始前核对匹配 task/attempt/phase/run/subject 的**原始用户回应**、固定输入及撤权状态，
并核验集中资源预约及实际写权。缺项时展示本阶段目标和缺项后等待；
已有明确确认不要重复盘问。无任务时返回总入口定位，不在阶段 Skill 中新建。

## 当前 run

1. 固定用户问题、目标、范围/非目标、约束和预期产物；Plan 未获准前只沟通，不生成业务模型或写代码。
2. 读取[Plan 方法](../../ontology/process/flow-plan.md)与[三场景义务](../../ontology/process/work-scenarios.md)；按 task.scene 只读对应场景 Skill 的“阶段方法”，不重新触发其建任务分支。
3. 固定需求和事实来源，区分事实、假设和未知；调查事实归 Agent，方案取舍和范围决策归用户。
4. 列出真实交付、对象路径、AC/oracle、正反测试、业务/记录写域、资源保证和停止条件。
5. 每个执行步骤写明具体操作、预期结果和验证方法；禁止用 TBD/TODO、“之后实现”、“添加验证”、“处理边缘情况”等占位语句冒充计划。
6. 将可在同一 Do 中独立执行的部分定义为 **Do-only Work Unit**；每个 Work Unit 写明输入、输出、作用域、资源、终止条件、完成条件和证据要求。
7. 正式子节点 seed 必须先能回指固定 ontology/work instance 中的具名 object/node、与当前节点的语义关系和适用 constraint，再同时具备独立职责、固定 I/O、可独立拒收成果与验证边界。仅有代码结构、LOC、工时、token、并行度或 Agent 置信度不能产生正式任务。
8. Plan 获批准后范围冻结。后续 Do 若新增产物、改变 AC/oracle、扩大写域/资源或引入不可逆副作用，必须停止并重新取得用户明确操作。

## 决策复杂度

当多个决策互相依赖时可建立设计树：只向用户展示当前前沿中的真实决策；
事实性问题由 Agent 自查。用户回答后更新前沿，直到没有未决决策。
不要为机械步骤强造选择题，也不要把推荐项当用户决定。

## 正式节点与 Work Unit 的边界

- **正式工作节点**：由固定 ontology object/work instance 与语义关系产生候选，并满足独立职责 + 固定输入/输出 + 可独立拒收成果 + 独立验证边界。Plan 只产生 seed；用户批准后由 fresh Agent 执行完整 PDCA，CONTEXT-01 从该节点选择 minimum sufficient ontology subgraph。
- **Do-only Work Unit**：只是当前任务 Do 内的执行切片，不创建 task/attempt，不拥有 Plan/Check/Act。
  它遵循 [CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 的
  `C=(I,O,S,R,T,Φ,Ψ)`，可内联或委派，但不能扩张父 Do 的授权。

详细设计见[Do 工作单元与正式节点拆分](../../docs/superpowers/specs/2026-09-15-subtask-splitting-design.md)。

## 自审

Plan 完成前确认：每个需求有 AC/验证；无占位符；依赖明确；每个交付可验收；
Work Unit 不越界；正式子节点有明确 ontology 来源关系、独立拒收理由和上下文边界；没有未批准范围。

## 报告与停止

保存 plan、固定输入、验收基线和必要 seed，标记 `phase_completed`，报告 Do 的固定对象、
写域和限制，然后**停止**。Do 的 `phase_start` 必须来自 Plan `phase_completed`
之后的新用户操作；Plan 期间的预批准、最初“开始”或 future blanket approval 都不能启动 Do。

**幂等性：** 重复 Plan 从固定输入恢复，不依赖中断前的隐式上下文，不重复创建产物。
