---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 原生派发契约 v4

TASK/CAP/CONFIRM/SCHED 是正式 PDCA 任务的依据。除唯一 root modeling bootstrap 外，
正式 task 必须已经绑定固定 ontology/work node，并由 CONTEXT-01 选择 minimum sufficient ontology subgraph。
root bootstrap 则绑定固定 root_seed_ref 和受控初始事实集。父 Agent 不监控生命周期、不指挥阶段、不代答；
宿主原生机制维持消息和资源。每阶段启动仍由用户决定。

## 适用范围

本契约适用于正式 ontology-backed work node / scene task，以及唯一的 root modeling bootstrap task。

当前 Do 内的 Do-only Work Unit 不是正式任务；即使 Work Unit 被委派给隔离执行者，
也遵循 [CONTRACT-01](../concept/pdca-execution-contract.md)，不创建 node/task/attempt，
不要求该执行者运行 Plan/Check/Act。

Work Unit 发现模型缺口时，把证据交回原任务并停止超出 Contract 的动作；原任务按
[EVOLVE-01](../concept/ontology-evolution.md) 区分内部细化、修订建议与职责变更，
不因出现新关系端点就自动启动 modeling。只有符合 [DECOMP-01](../concept/task-decomposition.md)
且已有固定模型来源的正式节点候选，经用户批准创建后才进入本契约。

## 用户显式创建正式任务

### 派发前固定

创建前必须固定：

- task_id / attempt；
- project/work；
- 普通 task 的 ontology revision / tree revision / node_id；root modeling bootstrap 则固定 `root_seed_ref`，并允许这些模型字段暂为空；
- scene；
- 普通 task 的当前 node responsibility、I/O、AC/oracle；root bootstrap 固定预期模型与 modeling AC；
- 普通 task 的 parent seed / composition relation；root bootstrap 无父节点时保持空；
- 普通 task 的 dependency refs 与固定 deliverables；root bootstrap 仅使用已明确允许的事实来源/复用定义；
- [CONTEXT-01](../process/select-task-subgraph.md) 选择出的 input/definition/context refs；
- allowed record/product scope；
- creation authorization ref；
- 唯一 dispatch_request_id。

不得以“父 Agent 已经知道”为由省略固定输入，也不得把父完整 conversation 当 assignment。

### Fresh Agent 与上下文隔离

正式 task 使用真实新 Agent/会话，不用同一主上下文换角色。
普通 ontology-backed task 只接收 assignment 中具名固定材料和必要公共规则：

```text
ontology node
+ minimum sufficient ontology subgraph
+ fixed parent boundary
+ required dependency deliverables
+ shared invariants
+ scene inputs
+ current task/authority
```

默认不传：

- parent/sibling 完整对话；
- 兄弟任务中间状态和调试历史；
- unrelated ontology branches；
- 未采用 reference；
- 全部项目历史。

root modeling bootstrap 的 fresh context 只含 root_seed_ref、允许事实来源、已采用定义、项目绑定和必要 modeling/PDCA authority；不得因尚无 ontology subgraph 就传整个项目历史。

如果宿主无法证明 fresh context 或无法限制输入，保持 blocked_unexecuted；
不能用“提示 Agent 忘记前文”冒充上下文隔离。

### 用户控制

用户决定创建哪些具名 node/scene task；ready 只是可启动条件，不是派发指令。
一次明确操作可创建若干已经定义且用户点名的 task；每个新 Agent 创建后先展示自己的 Plan 目标，
等待该任务的 Plan `phase_start`，不能因为“创建已批准”直接跑四阶段。

父 Agent不轮询监工、不推进阶段、不代写结果。child 可以在自己的 modeling task 中提出新的 child seed，
但不能自动创建后代。

### 原生创建

派发前集中登记并取得本任务 record/control scope 的实际写权。
创建结果 unknown 时保留可能占用，只对账原 dispatch_request，不能重新创建绕过。

取得原生创建回执及实际 Agent/conversation 身份，关联
[assignment](record-shapes/agent-assignment.md) 与 [dispatch](record-shapes/dispatch.md)。
正式任务必须可与用户交互、等待后继续原实例、写自己的记录区。

没有可交互、可恢复或可隔离上下文的宿主能力时，保持 blocked_unexecuted；
可以输出非正式分析，但不能冒称正式 node 已执行。

## 四条路径

| 路径 | 处理 |
|---|---|
| 新建获准 | 原生创建一次；固定 assignment、身份、receipt；新 Agent 展示 Plan 目标后等待 |
| 继续原任务 | 定位原实例，投递真实用户消息；核对 task/attempt/context 身份与权限连续性 |
| 创建结果 unknown | 保留原请求与可能占用；只对账，不重新创建、不分配新 attempt 绕过 |
| 恢复失败/返回新实例 | 阻断；新实例不接管，停止未获权动作并记录副作用 |

父 Agent 不保持等待循环或后台监控。任务完成/请求确认由宿主事件或用户主动打开会话呈现；
没有事件推送时明确限制，不伪造后台持续运行。

## 结果消费

父/组合任务只消费 child 的固定输出、interface、version/digest、evidence 与正式事件。
不导入 child 的完整活动历史来“帮助组合”。

task_id/conversation/attempt/ontology revision 不匹配的迟到返回不能覆盖当前 task。
源 node/revision 变化时按 DEPENDENCY-01 / CONTEXT-01 标 stale，再由用户决定后续动作。

按需看[原生能力说明](../concept/capability-protocol.md)；它不是运行兼容保证。
