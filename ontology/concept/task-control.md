---
schema: pdca.asset/v2
id: ontology:concept/task-control
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 任务控制事件、取消超时与安全接续
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-phase-status
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/pdca-recovery
  - ontology:concept/resource-ownership
control_spec:
  schema: pdca.control-event/v1
  adds_method_phase: false
  stop_state: stopping
  terminal_state: interrupted
  wait_modes:
  - explicit_wait
  - deadline_interrupt
  request_terminal_states:
  - consumed
  - expired
  - cancelled
  - superseded
  response_cutoff: host_decision_time < deadline
  control_owner: trusted_host_single_writer
  interrupted_requires:
  - execution_revoked
  - record_writer_released
  - inflight_settled_or_isolated
---

# 任务控制：停止、超时与安全接续

## CONTROL-01：控制事件不是方法阶段

本规则只约定宿主事件和Agent如何协作，不提供执行器。方法生命周期仍是四条正常边；取消、期限到期、能力丢失/恢复、写权交接、请求终局属于control事件。正常完成仍完整PDCA；被取消的尝试明确未完成，不生成虚假Check/Act/Archive。

宿主控制事件唯一写入者必须是实际可信机制，不是另一个决定业务结果的父Agent。用户可独立联系当前任务，路由者不代答、不改变语义。生命周期规则版本在派发前固定，Plan再固定业务基线；因此Plan尚未确认时也能合法取消。

## 记录与并发写入责任

`control/events/<event-id>.md`只追加事实，event_id唯一，control_revision由该任务宿主事件所有者在实际串行/事务边界递增。事件固定task/attempt、kind、source_ref或已授权policy_ref、前一事件、观察到的last_transition、在途operation和真实后端回执；自身digest只由后续对象引用。

`control/runtime.md`是可重建的宿主控制视图（execution_allowed、stop_pending、record_owner、terminal_receipt、保留资源），不让两个主体共写task.md。Agent持有记录写权时自行同步自身快照；宿主先写控制视图并撤销执行准入，只有实际撤销Agent记录写权/完成交回之后才能修复或封存task.md。原始阶段回执和失败证据不覆写。

普通阶段推进不是宿主语义审批；Agent判断门禁。需要硬性防止“核验之后发生取消却仍提交”的任务，宿主必须将control_revision/写权校验与阶段提交或副作用准入放在同一可排序的执行边界。只有文件读写、没有这个保证时，仅允许契约许可的隔离/合作式场景，不能把两次读文件称为原子互斥。

## 停止的明确步骤

1. 核验真实用户取消/替代消息，或派发前已授权的deadline_interrupt策略，或不可恢复事件。持久化stop_requested；停止作用于当前task/attempt，不推及无关兄弟。
2. 控制视图置stop_pending、execution_allowed=false；当前执行状态为stopping。立即不再发新的业务动作，不再提交下一PDCA边。已经在途的动作保留operation_id，发送取消不代表对方已经停止。
3. 保全当前版本/最后合法转换、请求与测试结果。撤销业务执行准入、检查旧Agent/子进程/远端调用，收集停止与写权撤销的真实回执。停止/对账/隔离动作必须有既有授权；需要额外破坏性清理时停并请求授权，不借取消扩大权限。
4. 对每个inflight操作查询目标结果：completed/cancelled_before_effect可结清；结果未知时隔离整个影响域并保留资源。仅有超时、心跳丢失、已删锁文件或进程名不存在都不是远端无副作用证明。
5. 执行者已失去继续作用能力，记录写权已合法交回，且每个未知影响已结清或可靠隔离后，写不可变termination回执。保留最后有效phase，execution_state=interrupted，terminal_reason如user_cancelled/deadline_exceeded/superseded/unrecoverable。
6. `interrupted`不等于所有资源释放。RESOURCE-01单独标注retained/released；未知影响资源仍保留，只有证明新任务不与其冲突或已完全结清，才允许相关后继启动。停止无法证明时保持stopping；宿主故障恢复先重建控制事实，不伪填终止。

未启动/派发失败也可取消：宿主证明不存在已派发或潜在未知执行者后封存Plan为interrupted，不能把“spawn请求超时”当作未派发事实。正常archive之后迟到取消只作事件记录，不重开终态。

## 请求期限与终局排序

等待策略由派发前已授权工作/宿主配置固定：`explicit_wait`表示无自动期限且始终可取消；`deadline_interrupt`需要policy_ref/version/真实授权、宿主计时基准和request截止值。不得猜测用户永久放弃，未配置时不擅自选择deadline；explicit_wait也应明确记录为所采用的保守策略，不伪造授权。

每个request的deadline在创建时按固定策略具体化。宿主采用同一可信计时域：决策提交时刻严格小于deadline才可接纳回应；等于或超过截止时刻视为到期。客户/Agent自填sent_at不具有排序权，排队但未在截止前被提交的回应不能追溯批准。宿主重启导致计时域无法连续核对时停止消费并核实，不猜剩余时间。

请求状态pending只能由一个终局取代：consumed（含confirmed/rejected/needs_change/clarification_answer）、expired、cancelled、superseded。真实来源、对象身份匹配且未终止时才能消费；相同终局重复事件返回原决策，不同事件不覆写。接收消息不等于消费：request-decision由可信消息机制持久化，Agent只引用它推进。

confirmed先于deadline合法消费，则该请求后续到期事件无效；deadline先终结则迟到confirmed不复活旧请求。任务取消是独立的任务控制事件：即使请求先consumed，也可以停止尚未结束的任务。阶段提交前必须重新核对有效控制资格；已合法提交的边保留，之后停止于该phase。若没有可核验的单一事件次序，阻断而不是让Agent比较壁钟决定赢家。

工作级tree_confirmation也适用请求终局排序，但主体为work/tree/proposal：过期只使提案保持未冻结/禁止其发布，不把已结束的节点任务改成interrupted；没有额外节点Agent任务。重新确认须新请求，内容变化须新proposal。

## 能力丢失、恢复与blocked解除

检测到权限、工作区、测试环境或宿主身份改变时，记录capability_lost，停止受影响动作并核对在途操作；不是所有能力丢失都自动取消任务。非终止blocked只有在CAP-01新证据覆盖原blocked_reason、RESOURCE-01写权仍有效或重新取得、原契约/授权未扩大、同一Agent确实可恢复时，才能由宿主解除准入阻断、Agent继续原phase。

如果测试环境仅影响测试，仍有安全的记录/用户通道，可按GATE-01记录error/blocked并诚实进入Check；这不会使失效测试可执行，也不能支持成功交付。无法安全恢复则走stopping→interrupted；终止attempt不复活，新的attempt必须新Agent。

## 后继attempt

正常路径：真实Check确认→Act→Archive→写权/资源结清→新attempt。异常路径：真实取消/替代/授权期限→安全终止→旧写权与冲突影响结清→新attempt。取消不是后继工作授权，新attempt仍需要自己的派发依据与Plan确认。

禁止Agent仅为了逃避Check确认自行取消并继续修改；提出返工建议不代表新任务已启动。新旧task/attempt/Agent和失败链均保留。不能通过“恢复”跨任务复用上下文。

模板：[事件](../../templates/control-event.md)、[控制视图](../../templates/control-state.md)、[终止](../../templates/termination.md)、[等待策略](../../templates/wait-policy.md)、[请求决策](../../templates/request-decision.md)。
