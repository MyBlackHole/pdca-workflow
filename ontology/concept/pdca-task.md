---
schema: pdca.asset/v2
id: ontology:concept/pdca-task
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.10
summary: 每节点完整任务与全新自主 Agent
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-14'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-tree-scheduling
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/pdca-recovery
  - ontology:concept/task-record-identity
  - ontology:process/independent-work-review
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/pdca-phase-status
---

# 每节点完整任务与全新自主 Agent

## TASK-01：任务单位

工作目标树中的每个节点，包括根与内部组合节点，在每个场景、每个attempt对应一个完整PDCA任务，不得合并多个目标节点或只派发叶子。任务键与冲突规则见TREE-01/SCHED-01。知识库引用、单条约束、一次工具调用不是额外目标节点，作为本任务内步骤；不能以此取消实际树节点的任务。

宿主在Plan前一对一分配真实全新Agent；同一任务在该上下文自主完成Plan/Do/Check/Act。Do不重复spawn；原任务恢复不是跨任务复用。新attempt必须新Agent，不得续用已归档/其他场景/其他节点的活动上下文。

## 自主执行与独立交互

宿主只准备具名初始输入、派发和消息路由，不替Agent完成Plan。Agent取得真实绑定/写入权后，派发方停止该任务的步骤控制，但继续调度其他就绪任务、路由各任务消息和更新工作索引；不得把交接理解为宿主等待该任务结束才派发兄弟。父本体节点是后续组合工作，不是常驻审批者。

Agent自行依据GATE-01推进阶段，Do→Check不要求父Agent或协调器审查回执。独立符合性审查属于REVIEW-01第三场景的新节点任务，不阻塞执行任务内部循环以形成父控制。

每个任务有独立conversation_ref和消息路由，用户可直接定位并交互；统一主界面可以无损转发消息，但不得由父Agent代答、过滤决定或重新批准。CONFIRM-01规定真实确认；等待只暂停对应任务，无关ready分支可继续。

## 隔离输入

仅导入当前节点、必要约束、明确授权的固定交付物/证据以及当前任务自身记录。禁止继承主会话、兄弟任务和前次attempt的完整活动对话。历史失败/修复建议可作为具名固定输入，不含原Agent隐含推理；新Agent独立核验。

公共规则、具名目标代码和固定交付可以共享，但宿主初始化参数、实际委派内容、预加载材料及共享记忆不得重新导入未选定的主/兄弟/旧 attempt 活动状态；不能用新 ID 自证输入隔离。Agent 类型/角色名不是实例 ID。宿主只能改会话名字、不能阻止自动继承历史上下文时，隔离不满足。无真实spawn/独立会话交互能力则blocked_unexecuted，不在主Agent中模拟完整运行。

## 派发未知与写入权

spawn前固定协议版本、已授权wait-policy、dispatch_request_id和任务键，按RESOURCE-01取得槽与私有记录区；成功后真实回执记录agent_id、隔离依据、工作区、conversation_ref、writer交接。超时先查实际创建结果；结果未知不盲目再建。新Agent只有取得同task_id写权才开始。

| 区域 | 写入者 | 其他主体 |
|---|---|---|
| task.md、tests/runs、evidence、conclusion、transitions、产物 | 当前绑定Agent | 只读固定交付物；宿主交接前可初始化 |
| control/requests | 当前Agent | 用户/可信消息通道读取 |
| control/responses | 可信消息通道，保留真实用户来源 | Agent核验后消费，不能自签 |
| control/dispatch.md、events/decisions/runtime、termination | 可信宿主控制机制 | 当前Agent只读实际控制事实，不代签 |
| 工作清单/发布索引 | 宿主单写者 | 节点只提交固定交付事件，不并发覆写整树 |

当前Agent持有记录写权时宿主不共写task.md，只用控制视图阻止动作；交回/撤权后宿主可依据真实回执修复或封存快照。具体停止、阶段竞争与资源保留只依CONTROL-01/RESOURCE-01。新attempt需SCHED-01完整准入，不以active作为锁。

## 完成与中断

父/孩子的任务依赖只决定何时能启动及导入何种产物，不能决定另一个任务phase或代其验收。每个任务的Check/Act完成不自动说明最终工作成功。

正常归档需四阶段回执；取消、崩溃且无法恢复时先按CONTROL-01安全stopping再在原phase记录interrupted，不造假补齐流程。新attempt按RECOVERY-01/REWORK-01接续，不把中断尝试隐藏。


状态只使用STATE-01矩阵。完整PDCA是正常任务的要求；安全中断明确未完成，不能为了凑流程在用户取消后继续业务。host事件/消息路由不替Agent做语义审查，也不创建无节点“控制Agent”。

<a id="task-full-assignment"></a>
## 整任务派发，不是阶段外包

正式派发的最小单位是一个 `(work_id, tree_revision, node_id, scene, attempt)` 的完整 PDCA，不是单次查找、摘要或 Do-only Work Unit。根同样由真实新 Agent 执行；只建立七个目录、七个称谓不产生七个任务执行事实。宿主可以装配初始目标、固定输入和记录区，但不得先替节点完成 Plan 再让子 Agent 补 Do，也不得在子 Agent 返回摘要后替它补 Check/Act。

初始任务书使用[全流程任务书](../../templates/agent-assignment.md)，按[派发记录关联](../contracts/agent-dispatch.md)绑定当前派发请求、固定协议、唯一节点场景、初始输入和专属资料区；任务书中的计划不是能力证明。原生创建回执须证明交付的是此任务书的精确版本，实际绑定后的 autonomy_evidence_ref 证明同一上下文可继续/恢复全部阶段并路由该任务确认。需要挂起等待用户是合法的，不要求一次工具调用内跑完；结束即丢上下文、不能继续的摘要工具不满足此合同。

同一上下文指同一逻辑 Agent/会话绑定和可恢复的任务状态，不要求同一 OS 进程永不退出。正常挂起、压缩和重启可沿原绑定恢复；恢复只返回相同名字/ID而不能恢复必要状态也不合格。恢复工具若新建了实例，不能改写原 dispatch 使它冒充原任务；具体处置见[原生恢复核对](pdca-recovery.md#recovery-native-binding)。

已有有效派发绑定的子 Agent 直接核验并进入自己的 Plan，不重新派发自身，也不换名另建根任务。Do/Check/Act 不重复 spawn；正常恢复只恢复原绑定。新的节点/场景/attempt 才由宿主按 SCHED 派发；本任务产生新 seed 后由宿主在父局部交付合格时接续，而不是让当前任务承载所有后代。

核验每阶段的真实执行者及 task/attempt/conversation/writer 的连续性，不能只检查阶段标题或由同一宿主补写的回执。缺原生事实返回未证明；若只允许候选资料保留，它不具备正式 Plan、Act、archive 或 delivery_usable 资格。真实中断按 STATE/CONTROL 留在实际阶段，禁止以“Act草稿”“确认已消费”豁免缺项。
