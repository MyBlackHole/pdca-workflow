---
schema: pdca.agent-assignment/v1
extension_revision: agent-dispatch.1
protocol_revision: 3.4.11
dispatch_request_id: null
work_id: null
tree_revision: null
node_id: null
scene: null
task_id: null
attempt: null
protocol_baseline_ref: null
protocol_baseline_digest: null
input_manifest_ref: null
input_manifest_digest: null
project_context_ref: null
project_context_digest: null
parent_delivery_ref: null
parent_delivery_digest: null
wait_policy_ref: null
wait_policy_digest: null
record_scope_ref: null
slot_ref: null
current_acceptance_ref: null
current_acceptance_digest: null
required_phases:
- plan
- do
- check
- act
confirmation_edges:
- plan_to_do
- check_to_act
---

# 给独立节点 Agent 的完整任务书（固定后派发）

你负责上列唯一节点、场景、attempt 的完整 PDCA，不是父任务的 Do-only 助手。先核验宿主真实 dispatch、agent/conversation 与写权绑定；同一上下文负责四阶段和自己的记录，既不派发自己也不接管兄弟。固定任务书不是 Plan 基线、批准或已执行证据。

## 初始目标与禁止事项

写明原目标/父seed、需交付的工作产物、必要动作、约束和可检验信号；研究对象与本次工作产物分别写。根 parent_delivery 为空，仅当身份/初始来源确为根时合法；孩子必须引用合格父局部交付。初始输入不得包括主/兄弟/旧 attempt 全量活动会话；列明实际传入的文件/文本版本和获准公共规则、预加载/记忆范围。历史继承参数未核实或初始化来源未知时不得自称隔离。

## 四阶段与消息

Plan：独立细化当前节点合同与当前验收、固定基线，请求本任务 Plan 确认。Do：仅在合法门禁后按目标和预算执行并保存实际观测。Check：自己核对每项验收与版本、保留失败和反例，固定结论包并请求本任务 Check 确认。Act：合格后自己收尾交付/四边/记录写权；失败或停止按原规则，不把正式缺项叫草稿归档。父/宿主不得替这些阶段。

## 固定双根与资料

从 project_context 读取已固定双根，不从本 Agent 默认 cwd/环境重新推导。业务命令只在 TARGET_ROOT 获权区；全部流程资料在 PDCA_ROOT 的本任务获权区。共享索引由宿主维护，不授予节点全库写权。

## 返回与等待

按 wait_policy 保持本任务身份，发送可路由的请求而不是让父代答。返回消息必须明确当前阶段、真实请求/产物引用、阻断项；只有实际完整链与可用固定交付才宣称完成。目录和摘要消息都不是终态。

## 跨等待继续，不重建执行者

后续消息继续原 task/attempt 与原生会话，不为 Do/Check/Act 再创建 Agent。身份或状态无法核对时，保持真实阶段并报告缺项；恢复误建的新会话不能执行原任务。用户确认必须仍指向当前任务/对象，宿主仅转发，不补阶段。原始恢复与异常返回进入获权控制记录，不能改写本固定任务书伪装创建时已知。
