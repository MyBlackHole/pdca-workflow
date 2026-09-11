---
schema: pdca.asset/v2
id: ontology:concept/work-ontology-tree
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.2
summary: 工作目标本体树：身份、组成与冻结
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-node-contract
  - ontology:concept/task-rework
  - ontology:concept/pdca-task
  - ontology:process/work-scenarios
  - ontology:concept/work-dependency-graph
  - ontology:concept/task-control
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
tree_spec:
  schema: pdca.work-tree/v3.4
  single_root: true
  unique_parent_except_root: true
  reachable_all: true
  composition_acyclic: true
  frozen_content_immutable: true
  mutable_view_in_signed_closure: false
  immutable_spec_schema: pdca.tree-spec/v1
  manifest_schema: pdca.tree-manifest/v1
freeze_spec:
  owner: host_work_publication_event
  request_schema: pdca.tree-confirmation-request/v1.1
  request_kind: tree_confirmation
  task_scoped: false
  requires_all_modeling_deliveries: true
  requires_current_closure_digest: true
  requires_dependency_check: true
  requires_request_decision: true
  response_identity:
  - work_id
  - tree_revision
  - proposal_id
  - request_id
  - work_conversation_ref
  - manifest_digest
  requires_real_source: true
  response_value: confirmed
---

# 工作目标本体树：身份、组成与冻结

## TREE-01：树，不是任选的执行投影

每个 work_id 的每个候选树版本 tree_revision 有唯一 root_node_id。除根之外每节点恰有一个 parent_node_id；所有节点从根可达，组成无环、无孤立节点、无重复 node_id。parent/children 必须互相一致。知识类的继承、接口引用、跨节点输入依赖不是组成父边，不能借其制造第二父归属。

工作实例位于 `records/works/<work-id>/trees/<tree-revision>/`。tree.md 仅保存可重建工作视图（根、索引、固定提案引用），不作为被签认的目标内容；节点按 NODE-01 保存，分片索引允许，但最终树清单必须覆盖全体。目录深度不决定父子关系。

## 定义、出现位置与任务身份

- definition_ref 标识可复用知识定义的固定版本；node_id 标识它在本次树中的出现位置。相同类可出现多次，各节点有独立任务和不同产物。不能把两个位置的产物重复算作两次交付。
- 同一物理共享实体只有一个写入所有者，在一个节点归属；其他节点用显式固定接口/输入引用。不能克隆两个“独占写入”的所有者。
- 任务键是 `(work_id, tree_revision, node_id, scene, attempt)`，task_id 是真实唯一运行身份。某节点引用十条知识约束仍是一个节点任务；十个目标节点必须有十个任务，不能合并成一个。

## 候选树启动与冻结

根建模任务以用户目标、授权和通用建模测试为输入，不要求已经存在自己的完整定义。根任务产出当前节点定义及直接子节点 seed；子任务在父 seed 被确认/交付后展开自己，不把所有后代塞进根上下文。

建模时先分配候选 tree_revision；节点 seed 身份、父归属和生成任务在建立后不可偷偷重定向。已封存节点内容用新 node_revision 修订；需要返工时按 REWORK-01 建立同节点新 attempt。受影响的已生成孩子必须重新验证父输入，不能继承过期 seed。

整树冻结要求：所有节点建模任务交付可用；每个必需父目标有唯一负责子节点或本节点组合义务；没有未定义必需孩子；全部节点正反例/测试 oracle/组合契约明确；预算满足；DEPENDENCY-01场景/跨场景图已核查且完整清单固定图与检查回执。先固定节点与用例内容，再固定闭包清单，真实计算摘要，最后通过下述唯一工作级路径关联真实用户的整树确认。冻结清单不引用自己的摘要或未来确认记录。

构建完整索引与比对身份可以使用通用宿主工具；工具的结构检查不是语义覆盖证明。节点内容审查按局部任务分摊，根不必读取所有后代正文。整树冻结采用下述宿主发布事件，不建立无节点业务任务、不重新激活根Agent。该事件只能装配和校验固定清单；发现语义缺口时由相应节点新完整PDCA处理，宿主不能代做建模。

## 变更与失效

冻结后不就地覆盖节点/测试集。变更产生新 tree_revision，给出旧→新节点映射、约束变化和影响集合，并重新确认。每个新版本仍有逐节点逐场景任务覆盖；未变内容可以作为固定输入复用，但新任务必须实际核对适用性，不能复制旧成功回执。

旧版本的任务、失败和结论保留；新版本未通过前不得宣称旧目标已被修复。单纯实现修复且目标/测试规范不变，用原 tree_revision 的新 attempt；判定规则改变则是目标变更，不是普通修复。

## 上下文界限

每节点声明上下文预算与直接子节点上限依据；以可实际读取并推理的内容为准，不按固定 token 数虚构能力。叶节点的实现与测试可独立完成；内部节点的接口组合和测试也必须有界。宽根/过大节点在建模期继续拆分，新增节点各自完整 PDCA。

树的总体大小不等于单任务上下文大小。固定索引可很大；任务只加载当前节点、适用祖先约束、直接孩子交付摘要和必要原始证据。上下文选择不能静默丢掉约束。


## 唯一冻结路径：工作级 tree_confirmation

1. 全部建模节点已正常结束、交付可用。先按本节点“固定目标与可变视图”固定tree-spec；宿主工作索引的唯一写入者装配`manifests/<proposal-id>.md`：work_id/tree_revision/root_node_id、tree-spec引用及摘要、完整node/suite/父子边清单及各对象digest、建模交付和终态回执引用、需求归属与局部语义审查证据。大树可以固定分片清单，但最终传递闭包必须完整；索引校验不能代替局部语义审查。
2. 清单不含自身digest、未来response或冻结receipt。宿主实际计算清单及闭包摘要，保存`control/tree-confirmations/requests/<request-id>.md`，使用`pdca.tree-confirmation-request/v1.1`。主体是work_id/tree_revision/proposal_id而非task_id；kind固定tree_confirmation；有独立work_conversation_ref。
3. 用户真实回应由可信消息通道保存对应response。必须同时匹配work/tree/proposal/request/conversation/manifest_digest，response=confirmed且source_ref可核验，并有CONTROL-01对应consumed请求决策且提案发布资格未被取消/替代；plan/check/clarification或旧根seed回答不适用。每次请求都有新request_id，同一proposal不可被另一个对象覆盖。
4. 消费前重读闭包、重新计算摘要并核查当前proposal仍相同；有修改、并发重指或未知状态则停止。确认通过才写`freeze-receipts/<receipt-id>.md`，同时引用清单摘要和真实response和request-decision以及已核查graph_ref/digest；最后更新tree.md工作视图。清单→响应→冻结回执单向引用，无摘要自引用。
5. rejected/needs_change保持未冻结；不在已归档根任务里追加伪造确认。仅解释不改字节可对同一proposal发新请求；内容变化必须新proposal并重新确认。需要语义改动时相关节点新attempt，已冻结树的任何目标变动则新tree_revision。

宿主工作事件没有PDCA phase，只承担TASK-01已有的索引与消息职责；它不是额外AI审查者，不创建第3N+1个无节点业务任务。能力缺失时保持未冻结。没有锁/事务时只能声明单写者尽力恢复；中断后验证manifest、response和receipt再重建视图，不通过写state=frozen自证批准。

模板：[请求](../../templates/tree-confirmation-request.md)、[响应](../../templates/tree-confirmation-response.md)、[冻结回执](../../templates/tree-freeze-receipt.md)。


工作请求的wait-policy由已授权工作配置预先固定。CONTROL-01排序confirmed/expired/cancelled/superseded；过期只保持提案未冻结，不影响已结束节点phase。冻结提交必须复核决策、当前proposal/授权图及停止视图：检查后发生取消或清单/图变动，旧检查不能继续发布。需要原子提交而宿主不支持时阻断，不能用重复读自称CAS。

## 多树共享知识与显式升级

definition_refs按REUSE-01固定library/ID/revision/字节及语义依赖manifest；tree冻结闭包还包含reuse-decision、local delta与adoption行。整树确认批准的是这些实际版本，不是以后自动读取latest。按ADOPT-01复核当前公告/采用资格，记录核对的知识视图generation；确认后发生相关阻断公告不能沿用旧检查发布。

不同工作可同时用同一不可变定义；相同physical实体的写域仍由RESOURCE-01管理。新head不自动修改已冻结树、不自动让未采用新版的旧证据stale；明确采用新定义/目标差异按本节既有新tree_revision规则处理。若旧定义已确认错误，保留旧字节同时按ADOPT-01通知/阻断/返工，不能以版本固定为由继续批准错误。

## 固定目标与可变视图：本节细化唯一冻结路径

`tree.md` 是工作视图；它的state、当前proposal、确认与receipt指针会变化。**禁止把该视图、控制视图、未来回执或自身清单放入已确认目标闭包。**使用独立的 `snapshots/<proposal>/tree-spec.md` 固定原目标来源、协议基线、被审对象、根/节点/父子关系、角色实例映射与知识义务；其中不含未来确认或发布state。目标spec不是节点完成证明。

`manifests/<proposal>.md` 使用tree-manifest模板，固定spec、所有node和三个scene套件/case/oracle/fixture、原始采用定义闭包、reuse/local delta/采用行、工作图及对应graph-check、每节点所选modeling task/attempt的固定delivery及独立终态证明。逐对象含role、ID、revision、固定ref、真实digest；task_id、attempt和来源不能混合。缺必要对象/占位摘要/不可访问source均阻断，不仅比较最外层manifest_digest。

计算顺序：节点本地payload与suite先固定→本地delivery固定→合法终态另存→图与check固定→tree-spec固定→manifest固定→真实请求/响应和消费决策→完整冻结提交→更新tree.md视图。图检查固定图digest，模型测试PASS不能替代宿主运行回执。确认和终态分别来源真实事件，用户批准不替代技术门禁。

父seed允许按DECOMP-01展开；整树spec解析每个实际node的唯一父和所有直接孩子，结果不是强制最初种子数。host只能装配已检查语义的精确输入，不能增加遗漏职责或把not_defined改成not_run。确认后任一固定对象变化均新proposal重新授权；已冻结目标语义变化新tree_revision。旧回执内容不覆写，旧错误另追加完整性事件；检查闭包不能靠重算并修改旧response来修复。

固定manifest内有若干同字节只读副本时视为同一对象，不产生第二权威；目标文件不存在/摘要不匹配时不可退回读取latest。同样禁止把静态图检查的部分场景范围当整树全部依赖完成。

模板：[固定目标](../../templates/tree-spec.md)、[闭包清单](../../templates/tree-manifest.md)、[工作视图](../../templates/work-tree.md)。这些新模板是草稿，不自动冻结、签名或提供事务。

## 先技术就绪，再请求整树确认

在发送宣称“可冻结”的请求前，固定[tree-readiness](../../templates/tree-readiness.md)，按清单实际字节逐项检查：

| 检查项 | 不满足时 |
|---|---|
| 所有node_bindings的node/delivery/terminal/suite ID在显式闭包内唯一可解析且身份一致 | terminal悬空、混attempt或revision冲突阻断 |
| 每节点三场景的有效case/input/expected/oracle/必需性和采用语义完整 | 只有名称或“同来源语义”阻断；未来实际run可不存在 |
| 项目subject快照成员完整，协议/业务定义/运行审查用途明确 | 单文件摘要冒充集合、别名不可解析阻断 |
| 全场景/跨场景图完整；graph-check固定实际graph摘要和覆盖范围 | 仅modeling图或外层hash正确不足以通过 |
| 所有影响当前冻结对象的阻断issue有有效处置，选定交付和独立终态有效 | 已知缺陷不得仅写“交以后复核” |
| 累计预算与本地义务完整 | 不以新attempt清零、删义务或强制判叶达标 |

readiness固定manifest摘要，放在被检查清单之外；真实请求引用它，防止循环摘要。readiness不是用户批准，用户批准也不能让技术缺项消失。准备讨论的草稿可发澄清，但不能标为ready提案。任一固定成员变化，新proposal/readiness/request；不能改旧response适配新内容。


<a id="tree-required-closure"></a>
## TREE-01 · 应有闭包与实有闭包分别核验

从 CONTRACT-01 的固定要求依据展开节点/场景/必需角色、终态、图及图检查。核对清单时先查整项缺失，再查每项字段、身份、摘要、依赖和有效结论；不能只遍历“实际列出来的对象”。节点定义本身也必须与 binding/delivery/terminal 的 node_id 对齐。可选对象、对象顺序和合法说明不得导致误拒绝。

readiness.required_checks 由适用权威谓词推导并双向核对；语义、真实确认或终态来源未核验时保持 not_ready。维护检查的结构关系 pass 不能写成生产 ready。分片须完整覆盖已确定集合；空 node_bindings、仅留场景标签的空图、整项删除 graph_check 都不合格。
