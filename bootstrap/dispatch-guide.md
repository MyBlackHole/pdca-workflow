# 原生全流程派发入口 · agent-dispatch.1

这是 TASK/CAP/SCHED 的动作导航，不是执行器、adapter、额外批准或新角色。沿用固定 PDCA_ROOT/TARGET_ROOT、协议、授权和 wait-policy。先核对 CONTROL/RESOURCE：停止、撤权优先，在途未知保留占用。

## 先分清接收者与派发方

**已有固定任务书、真实 dispatch/agent/conversation 和写权交接的节点：**核验身份、输入与当前控制，再进入自己的真实阶段；不再派发自身。收到继续消息先按 [RECOVERY](../ontology/concept/pdca-recovery.md#recovery-native-binding)核验，不重新创建根。

**准备和派发的宿主：**按 [CAP](../ontology/concept/capability-protocol.md#cap-environment-and-call)核实实际原生工具；需要操作某宿主时才读[原生语义说明](native-agent-notes.md)。工具名来自现场描述；加载 Skill、换角色名字或新建目录不等于创建 Agent。只支持一次性摘要、不能跨确认继续的工具不满足 full_pdca。

<a id="dispatch-four-paths"></a>
## 四条路径：先识别事实，再调用

| 当前事实 | 现在做什么 | 必须看到的结果；缺失时停止在哪里 |
|---|---|---|
| **新建**：新节点/场景/attempt，无在途创建，SCHED 准入成立 | 固定任务书、输入和 dispatch_request_id；取得槽/私有资料区；使用已核验的“不继承其他任务历史”方式创建。只传具名固定材料 | 原生回执关联同一请求/任务书/输入；取得真实实例及会话映射，再完成 writer 交接。返回类型名、摘要或自定义名字不够；未交接不能进入 Plan |
| **继续**：原 task/attempt 已有绑定且未终止 | 只调用继续原实例的原生动作；提交当前任务的消息/真实确认引用，先核对期望身份、最后合法阶段和控制/资源 | 返回或可追踪原生事件仍指向原 agent/conversation；状态可恢复、授权仍适用才能继续。相同 ID 但状态丢失也不能通过 |
| **创建结果未知**：超时/断线，不知道是否创建 | 保留原请求、输入、槽/作用域；仅查询、对账同一请求，按已授权等待策略处理 | 找到真实 accepted 后核验并交接；有明确 not_created 及结清依据才结束本次占用并重新准入。查不到、无结果、超时都不是 not_created，禁止盲目再建 |
| **恢复失败**：原会话不可达、身份不符或状态不足 | 不改绑、不让主 Agent 补阶段；保存实际返回。若工具误建新会话，将其作为异常实例停止/隔离并核查副作用，不交正式写权 | 临时未知可保持 blocked 并查原绑定；原绑定确实不可恢复时按 CONTROL 安全终止。新 attempt 只有在旧影响结清、SCHED 完整准入后才新建 |

上述分类不是新业务状态；沿用现有 dispatch/control/slot 记录。更换操作系统进程不必然更换逻辑 Agent；是否恢复由原生身份、会话状态和记录连续性共同证明。不能为每个阶段重新调用创建入口。

## 新建前的最小输入与结果消费

使用[全流程任务书](../templates/agent-assignment.md)：根导入原目标；孩子导入合格父 seed。固定 task_key、协议/双根、验收、输入清单、私有资料区、全部四阶段和两次确认。公共规则可复用；主动粘贴主会话、自动 fork 或共享记忆引入未授权活动状态都不合格。初始化输入未知记 unknown，不凭“fresh”字样通过。

按[派发模板](../templates/dispatch.md)关联原生创建参数/返回、环境核验、实际输入、身份和交接。检查的是本次事实，不能复用别的任务 spawn 回执，也不要求每任务重测整套宿主。没有真实来源只报告“未证明”。

## 交接后：任务自治，宿主继续调度

宿主继续提交其余已就绪、可容纳且不冲突的任务；记录未派发原因。一个任务等待 Plan/Check 确认不暂停兄弟；异步能力不足按授权容量运行，不冒充并行通过。只无损路由已具名的真实消息，不代答、不改写批准、不预批未来对象，不共写节点任务正文。

节点在原绑定完成 Plan→Do→Check→Act。Do 生成的 scene suite 与当前 ME 分别固定；只读研究不自动授权修改源码。父节点交付自身和直接 seed 后结束本地任务，后代由宿主按前置派发；缺陷以固定 issue 交回，不控制别的任务阶段。

宿主只依实际四阶段链、run、固定交付与独立终态决定采用。摘要、完成标记或四个标题不等于正常完成；真实中断留在原阶段。关联见[派发契约](../ontology/contracts/agent-dispatch.md)和[调度观测](../templates/scheduling-observation.md)。[有限回放与现场验收](../tests/agent-dispatch/recovery.md)必须分开报告。
