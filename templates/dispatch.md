---
schema: pdca.dispatch/v3.2
task_id: null
dispatch_request_id: null
agent_id: null
spawn_receipt_ref: null
isolation_evidence_ref: null
handoff_completed: false
coordinator_state: null
conversation_ref: null
autonomy_evidence_ref: null
writer_revocation_ref: null
capabilities: []
protocol_revision: 3.4.11
attempt: null
slot_ref: null
slot_claim_receipt_ref: null
wait_policy_ref: null
wait_policy_digest: null
control_owner_ref: null
pinned_graph: null
record_reservation_ref: null
capability_check_ref: null
guarantee_profile: null
protocol_baseline_ref: null
---

# 派发与写入交接

由宿主派发机制填写实际宿主能力映射和派发回执。请求ID在spawn前固定，agent_id必须来自真实工具。

## 能力映射

| 抽象能力 | 实际工具 | 状态 | 真实依据 | 限制 |
|---|---|---|---|---|

## 隔离和作用域

`isolation_evidence_ref`关联适用环境核验和本次实际初始化方式/输入清单：包括委派文本、历史继承参数、公共规则与记忆来源。新 ID、类型名或“fresh”自述都不证明隔离；缺事实记 unknown。

`spawn_receipt_ref`关联本次原生调用及返回；`agent_id`、`conversation_ref`使用实际映射。环境核验可按CAP范围复用，创建回执不能跨任务复用。原生响应只有路由句柄时，保留其与实例/会话的可核验映射，不虚造宿主未提供的标识。

## 交接

子Agent只在真实回执和writer交接完成后运行；派发方停止步骤控制由宿主保证。按[四路径](../bootstrap/dispatch-guide.md#dispatch-four-paths)处理：创建未知保留原请求/占用并查询；查不到不等于未创建。原会话继续须核对原 task/attempt、期望和实际 agent/conversation、状态、控制与写权。新会话不得覆写原绑定；恢复失败不由宿主补阶段。

`autonomy_evidence_ref`先关联环境中“同一绑定可跨等待继续”的实测依据，后由实际阶段/继续记录补足本任务连续性；不能在创建时声明未来四阶段已完成。不增加顶层字段，不把这段填写说明当作已经取得回执。

## 派发前控制策略

wait-policy必须先有真实授权和固定版本，明确explicit_wait或deadline_interrupt及期限/计时。先取得槽和私有记录区；业务资源在Plan确认范围后取得。旧attempt不安全时不得交接，未知spawn结果不重新创建。

协议版本由实际所选protocol-release快照确定；本模板默认值不是执行证据。schema/资产版本可以不同。派发前绑定记录未知字段不造ID，正式任务主记录仍在records/<task-id>/task.md。

## 全流程任务书与调度观测关联（agent-dispatch.1）

采用[关联契约](../ontology/contracts/agent-dispatch.md)时，创建前的[任务书](agent-assignment.md)由 capability_check_ref 所引 checks 中 `task.assignment` 项固定 ref/digest，并在实际 spawn_receipt_ref 中保留收到的相同任务书摘要；不要凭空添加未定义的 dispatch 顶层字段。capabilities 继续记录真实能力，autonomy_evidence_ref 证明整个PDCA在同一上下文可继续，不仅证明工具返回了文本。

对应 [scheduling-observation](scheduling-observation.md)用本 dispatch_request_id 与实际spawn回执关联。交接只停止派发方控制本节点步骤，不停止宿主派发其余独立任务。单次Do返回由父补阶段、根由主会话直接执行、子再spawn自己，均不满足TASK。
