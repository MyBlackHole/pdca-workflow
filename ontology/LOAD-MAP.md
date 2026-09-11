# 按事件定位权威条款

仅导航，不复制规则或生成简化权威。固定protocol-release版本；按当前scene/phase/事件读取正文，不按文件mtime选规则。CONTROL/RESOURCE的停止和撤权条件跨阶段始终适用，不能因按需加载而漏掉。

| 事件 | 必读权威 | 记录入口 |
|---|---|---|
| 派发/恢复 | [TASK](concept/pdca-task.md)、[CAP](concept/capability-protocol.md)、[SCHED](concept/work-tree-scheduling.md)、[RECOVERY](concept/pdca-recovery.md) | [能力](../templates/capability-check.md)、[派发](../templates/dispatch.md) |
| Plan/进入Do | [CONTRACT](concept/pdca-execution-contract.md)、[GATE](concept/pdca-gate.md)、[CONFIRM](concept/pdca-ai-friendly-confirmation.md) | [入口suite](../tests/modeling-entry/suite.md)、[基线](../templates/baseline.md)、[门禁](../templates/gate-check.md) |
| 建模/递归/复用 | [NODE](concept/work-node-contract.md)、[DECOMP](concept/task-decomposition.md)、[REUSE](concept/ontology-reuse.md) | [节点](../templates/work-node.md)、[采用](../templates/reuse-decision.md) |
| 测试/修复/证据 | [TEST](concept/task-unit-test.md)、[CASE](concept/task-test-case.md)、[REWORK](concept/task-rework.md)、[EVIDENCE](concept/pdca-evidence.md) | [run](../templates/test-run.md)、[增补](../templates/regression-extension.md)、[预算](../templates/work-budget.md) |
| Check/结束 | [VERDICT](concept/pdca-verdict.md)、[TRANSITION](concept/pdca-transition.md)、[CONFIRM](concept/pdca-ai-friendly-confirmation.md) | [结论](../templates/conclusion.md)、[终态](../templates/archive-receipt.md) |
| 冻结/工作发布 | [TREE](concept/work-ontology-tree.md)、[DEPENDENCY](concept/work-dependency-graph.md)、[REVIEW](process/independent-work-review.md) | [readiness](../templates/tree-readiness.md)、[release](../templates/work-release-manifest.md) |
| 取消/资格变化 | [CONTROL](concept/task-control.md)、[RESOURCE](concept/resource-ownership.md)、[STATE](concept/pdca-phase-status.md) | [控制事件](../templates/control-event.md)、[终止](../templates/termination.md) |
| 共享知识发布/采用变化 | [EVOLVE](concept/ontology-evolution.md)、[ADOPT](concept/ontology-adoption.md) | [知识发布](../templates/ontology-release.md)、[影响](../templates/ontology-impact.md) |

路径只定位；所有内容按本次固定协议快照读取。验证效果看实际注入上下文和漏约束，不用入口字节数直接推断模型质量。


## 细粒度定位与输出

| 当前问题 | 直接条款 | 最小输出 |
|---|---|---|
| 候选同步缩水、要求来源 | [CONTRACT 固定依据](concept/pdca-execution-contract.md#contract-requirements-basis)、[SCENE 集合](process/work-scenarios.md#scene-required-set) | basis 摘要、缺失义务、原文位置 |
| 正式模板类型或身份 | [CONTRACT 字段投影](concept/pdca-execution-contract.md#contract-fixed-records) | 文件/字段/expected/actual |
| 整树缺对象、空图 | [TREE 应有闭包](concept/work-ontology-tree.md#tree-required-closure)、[图全域](concept/work-dependency-graph.md#dependency-complete-check) | 缺失集合、端点/环见证 |
| defaults 或来源绑定冲突 | [CASE 展开](concept/task-test-case.md#case-deterministic-expansion) | 来源摘要、冲突字段、有效case摘要 |
| 阶段/版本错配 | [TRANSITION 链级](concept/pdca-transition.md#transition-chain-binding) | 首次断链位置、涉及版本 |
| 预算负值/重置 | [REWORK 计量](concept/task-rework.md#rework-budget-quantities) | 单位、账本范围、无效事件 |

导航不复制约束。读取既有条款时，CONTROL/RESOURCE 的跨阶段停止条件始终保留。机械摘要/图/集合核对用通用工具产出带文件位置的观测摘要；Agent 按需读取异常原文，不把大清单整段重复注入。实际注入量须由宿主记录，本包不把字节变化冒充token或性能改进。

## 记录字段按需加载

[字段类型索引](contracts/record-shapes/index.md)从CONTRACT正文移出；Plan只读当前baseline/request/gate类型，测试与Check读case/run/review，冻结再读tree/manifest。按需只改变读集，不改变必需义务。

[关系核对范围](contracts/record-relations.md)：观察身份、门禁当前对象、证据集合覆盖、树拓扑和manifest角色。输出缺项及未覆盖项，不能仅把整体pass复制到交付。

## 停止／失败／接续的按需记录检查

发生能力阻断、请求拒绝、停止或后继准入时，读STATE/CONTROL/RESOURCE/SCHED的现有规则与[生命周期字段和关系](contracts/lifecycle-records.md)。不在每次Plan预加载该附件。记录一致性、业务结果和生产资格分别输出；普通completed业务失败仍走四边。

## 从其他项目使用／双目录恢复

采用单变量工作入口时读取[project-workspace](contracts/project-workspace.md)及[任务上下文模板](../templates/project-task-context.md)。首次目标=入口真实cwd；PDCA根=非空PDCA_ROOT或同一cwd。固定后不随cd/子Agent环境变化。支持shared自维护与split跨项目；未设置且无有效入口时阻断。再走原Plan/Do/Check/Act，路径绑定不替代CAP/RESOURCE/CONFIRM，旧ref语义不改变。

跨项目启动失败先看[入口交接](../bootstrap/entry-check.md)与[故障定位](../examples/cross-project/troubleshooting.md)。定位规则、加载规则和具备执行能力是三项不同事实；不以任一项替代其它项。

## 根/独立任务实际派发与并发

读[dispatch-guide](../bootstrap/dispatch-guide.md)分清宿主和已有绑定的节点，再按[TASK完整任务](concept/pdca-task.md#task-full-assignment)、[CAP全流程/并发](concept/capability-protocol.md#cap-full-agent-and-parallel)、[SCHED先派发再等待](concept/work-tree-scheduling.md#sched-fill-before-wait)行动。记录类型按需用[任务书](../templates/agent-assignment.md)、[调度观测](../templates/scheduling-observation.md)和[关联契约](contracts/agent-dispatch.md)，不预加载所有后代规则。

## 当前方法的直接入口

| 已出现的条件 | 当前必读位置 | 结果写回哪里 |
|---|---|---|
| 建模需要决定节点/内部步骤 | [DECOMP 拒收见证](concept/task-decomposition.md#decomp-rejection-witness) | 原NODE.decomposition |
| Check或采用依赖产物 | [EVIDENCE 消费顺序](concept/pdca-evidence.md#evidence-consumption) | 原AC映射/conclusion |
| 核验一个可疑发现 | [REVIEW 反证](process/independent-work-review.md#review-counterevidence) | 原issues与审查正文 |
| 上下文压缩或恢复 | [RECOVERY 必要事实](concept/pdca-recovery.md#recovery-capsule) | 原恢复导航与真实记录 |

这些是既有权威内部的方法，不增加schema、审批、任务或新的必读目录。仅维护规则效果时才使用[行为评测](../tests/agent-behavior-eval/suite.md)。
