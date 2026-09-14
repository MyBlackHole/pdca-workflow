---
schema: pdca.agent-dispatch-contract/v1
extension_revision: agent-dispatch.1
protocol_revision: 3.4.11
authority_refs: [TASK-01, SCHED-01, CAP-01, CONTRACT-01, RESOURCE-01, CONFIRM-01]
assignment_template_ref: ../../templates/agent-assignment.md
scheduling_template_ref: ../../templates/scheduling-observation.md
adoption: pinned_protocol_snapshot
---

# 全流程派发和就绪并发：记录关联

这是现有权威的记录投影，不增加业务状态、审批者、工作流执行器或adapter。新的工作固定本附件及更新规则的版本/摘要；旧记录继续按原快照读，不能倒填当前协议或批准。原三场景、各节点完整PDCA和固定双根不变。

本文件 protocol_revision 标记所属发行投影，必须与采用的 protocol-release 一致。extension_revision=agent-dispatch.1 与记录 schema 独立，不表示只能采用最初发布时的协议号；旧工作仍固定旧文件字节。原有三场景和完整任务权责不变；3.4.10澄清原生继续身份/状态核对和环境证据复用范围，不能将旧记录倒填为新验收。

## 1. 两类新记录与已有模板的关联

`pdca.agent-assignment/v1` 固定在创建之前。非空字符串：dispatch_request_id、work_id、tree_revision、node_id、scene、task_id；attempt必须为非布尔正整数，scene只取已有三个场景。required_phases精确为plan/do/check/act，confirmation_edges精确为plan_to_do/check_to_act，禁止候选删减。

protocol_baseline、input_manifest、project_context、wait_policy、current_acceptance的ref/digest都必须可解析、摘要实算并符合对应task/attempt及原目标；record_scope_ref、slot_ref指向已有资源/槽事实。根才可无parent_delivery；孩子引用正常完整可用的父局部交付及其摘要。当前建模入口不能被Do生成suite替换。初始任务书不包含尚未取得的agent_id和未来批准；实际身份来自创建回执。

不向原 `pdca.dispatch/v3.2` 增加未定义顶层字段。沿用 capability_check_ref：checks中task.assignment项固定任务书；实际spawn_receipt_ref须记录原生请求/响应以及收到的同一assignment摘要。autonomy_evidence_ref证明同一绑定能自主继续完整四阶段，不以任务书的要求自证能力。agent_id、conversation_ref、handoff_completed、slot及graph等原字段照常核验。

`pdca.scheduling-observation/v1` 位于宿主获权控制/工作区。必须固定observation_id、work/tree、requirements_basis与graph及摘要、capability_check、trigger_event/ref/digest和事件排序来源。frontier、capacity_observations、decisions必须是逐项记录；前沿确实为空时[]合法，但须由独立basis核对。spawn_receipt_refs和next_wakeup_refs对应实际事实，没有创建或没有后继事件时明确为空及理由。coverage为complete/incomplete，只说明事件范围，不是业务成功。

候选身份用完整task_key；绑定任务书、dispatch、task、阶段、run、terminal、delivery和workspace同一身份。宿主的索引写入事件不能充作子Agent阶段执行事件。任务/场景/attempt/会话混用、父代写阶段、无来源确认、未核验“草稿可用”均不能采用。

## 2. 事件与快照单向固定

先固定初始依据、输入、任务书和派发请求；再记录原生提交/接受/未知事实；阶段原记录按其正常时点固定；最后用外层调度观测/轨迹清单关联。不要让被摘要的任务书引用未来包含它摘要的调度快照形成循环。

完整候选来自原目标/合格seed/授权图，not_ready的原因也必须具名。先按CAP核验真实容量与计量；等待确认默认仍占会话位，在途未知创建保留可能占用及scope。安全释放必须来自实际终态/撤权/结清事实，不能凭结束文字减少容量。

事件排序必须同一可核验时间/序号域，或有明确跨域因果映射。不得拿文件mtime或不可比较墙钟推断同时执行。指标区分已接受在途峰值、实际工作重叠、待确认会话和ready未派发；没有实际工作start/end只能报告重叠未知。

## 3. 有限离线重放格式

独立维护附件提供只读 `audit_dispatch.py`。它不创建Agent、不改目标、不路由批准、不认证宿主、不承担正式调度。它检查下面明确限定的**归一化投影**，不是正式task/transition等原记录的替代schema。原生导出应保留原字节、投影规则与字段映射；无法投影的事实返回未覆盖，不复制fixture。

独立传入 `pdca.dispatch-audit-basis/v1` 及其外部摘要，内容包含work/tree、固定双根、上下文摘要、真实容量/已占用、全体任务规格、任务书/输入摘要、依赖、已授权资源访问表、必需能力/状态、会话历史保留。basis不是从被审trace里反推；本工具只核对已输入事实间关系，不能证明basis反映真实宿主。

trace为 `pdca.dispatch-audit-trace/v1`，包含basis_digest、source_mode(synthetic/native_export/process_probe)、event_domain、coverage(complete/incomplete)、ordered events及raw_sources。每条event含唯一id、严格连续seq、kind、source_id；raw_sources固定其来源类型、规范化payload和摘要。source_mode/摘要是声明和完整性，不是真实性认证；任意补算hash都不能伪造生产资格。已知缺来源/序号缺口返回incomplete，不能把空issues视为pass。

| kind | 关联检查 |
|---|---|
| opportunity | candidates与当前所有未派发任务集合一致，含尚不就绪者，不由已创建目录决定；本事件开启一轮就绪检查。 |
| submit | request唯一、task未在途；原依赖已可用、授权/能力/容量/资源允许；输入/assignment/context摘要匹配。 |
| accepted | 绑定同一request、真实声明的agent/conversation、私有record_scope、输入/assignment/context；禁止活动上下文继承和跨任务身份复用。 |
| unknown / query / not_created | 未知保留资源与容量，查询同request；只有具名not_created/结清事实可释放，重新提交仍不得盲建新身份。 |
| environment / capability_check | 限定投影中记录环境变化与适用能力依据；旧依据不能证明新环境，仍非真实宿主认证。 |
| resume_request / resumed / resume_failed | 追加的有限恢复观测：请求绑定原实例，返回的期望/实际身份、状态连续性、环境依据及停止状态；误建新会话不能成为原任务写入者。不是新的正式记录schema。 |
| phase | plan/do/check/act职责事件顺序和actor/conversation与当前绑定一致；不是认证正文质量。 |
| pin / confirmation | baseline与review固定摘要不可漂移；确认来自独立user_source声明并绑定本任务、当前对象和对应边。 |
| run | 本任务、本attempt、本产物的实际观测声明；业务失败不必伪造pass。 |
| terminal / release / delivery | 正常四阶段及必要run/确认齐全才称completed；安全中断与正常失败不同；释放实际同owner/scope；usable要求正常合格交付，不能把draft作为前置。 |
| cancel | 当前工作授权的停止范围优先；相关任务不得继续推进，无关兄弟仍按自身条件判断。 |
| wait | 对照剩余ready任务、真实占用和冲突，不能仍有可提交者却等待；每个延期理由与实际条件一致。 |

本重放检查是有限离散事件模型：一次wait是一个可核验调度边界，不能用它判断任意毫秒级公平性。全量时间性能、真实隔离、授权和存储原子性均NOT_PROVEN。正常完成与事件窗口结束分开，prefix中仍在等待/运行可结构一致，不自动宣称任务成功。规范的四条实际转换链仍由原CONTRACT/TRANSITION和正式记录核验，投影phase事件不能替代它。

## 4. 输出与适用范围

逐检查组输出pass/fail/incomplete、不匹配位置、实际断言数和未覆盖层；overall只聚合已声明的有限关系，不输出正式PDCA通过。结构错误与证据不足分开，任何必需未知不升格pass。source_mode=synthetic或process_probe永远不产生生产资格；native_export也须另行认证原生来源，文件自述不够。

3.4.10独立附件首次配齐此分发集合中的 `audit_dispatch.py` 与 `run_dispatch_tests.py`，提供归一化反例/合法近邻和原始输入/预期/实际结果。它不重建曾缺失的旧工具或历史运行；不提供原生Agent或OS并发执行验收。精确字段与有界支持范围见附件 DISPATCH-FORMAT.md；旧59例的逐项映射与新增恢复控制分别报告，未覆盖项目不得算通过。正式宿主试点见[并发示例](../../examples/parallel-pdca.md)和[恢复验收](../../tests/agent-dispatch/recovery.md)。
