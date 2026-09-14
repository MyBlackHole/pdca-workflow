---
schema: pdca.asset/v2
id: ontology:concept/pdca-execution-contract
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.11
summary: 节点场景执行契约与不可漂移基线
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: '2026-09-14'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-node-contract
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/work-dependency-graph
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
record_shape_index_ref: ../contracts/record-shapes/index.md
record_shape_index_digest: 41d7aa0cb4b787438faf4661cd169eef47d327a5240e9641c226b220bf30ad3a
---

# 节点场景执行契约与不可漂移基线

## CONTRACT-01

每任务绑定一个目标节点和一个scene；四字段execution_contract必须非空：work_product（具名产物及位置）、required_actions（动作/测试/交付）、constraints（作用域/安全/本体义务）、testable_signal（具体观测/oracle/失败判据）。节点任务不可跨节点合并，工具调用是任务内步骤。

基线固定work/tree/node/scene/attempt、NODE-01定义或建模seed、AC、TEST-01套件与CASE-01有效案例、所需真实工具、写入范围、Do内修复预算与回归策略。建模任务的目标尚未完整定义，使用父seed/用户目标和通用建模规范作为输入，不能要求先有自己的成品。

## 冻结与确认

在artifacts/baselines/<baseline-id>.md保存不可变清单及定义/suite/fixture固定位置和真实摘要；全部生命周期规则也固定版本，可按阶段再读取正文。先固定对象后计算清单摘要，CONFIRM-01绑定该对象。

Do后允许登记非规范的补充事实和诊断回归案例，但不改变既有AC/expected/必需性。实现代码可在Do预算内修复，每次新版本/新run；基线与测试oracle不变。

改变目标、接口、权限、测试期望或必须覆盖是新基线问题：保留旧结果，按REWORK-01建新任务/必要时新树版本，不能通过放宽验收自救。Plan内尚未执行可修草稿重新确认。Check/Act不得回Do偷做实现。

测试绑定不能以平台差异改变期望语义；确认后的工具环境变动需核对适用性和重新产生证据，不能复用旧测试输出。


## 运行控制输入

Plan基线还固定pinned_graph_ref/digest与检查回执、真实资源作用域及保证等级、能力证据引用、派发前已授权wait-policy版本。实际reservation/epoch与短时能力回执可追加为运行事实，不能改变授权scope或图语义。每次使用前CAP/RESOURCE重新核对有效性；基线引用不把短时租约变成永久写权。

取消策略不等待Plan确认才生效；CONTROL-01已在派发前固定。缺图、真实写域、可执行必需测试或用户批准时不进入Do。若需要新的资源权限/依赖边，不能由运行重绑定偷偷扩权。

## 复用决定与采用基线

新baseline为pdca.baseline/v3.4。建模Plan固定modeling_decision_ref、候选definition_refs/manifest、局部变化意图和通用建模测试；Do生成的最终NODE不能反过来成为验证它自己的新Plan标准。其他scene固定最终定义/有效契约/套件/adoption refs。

改用其他定义版本或行为delta不是工具重绑定；按REWORK/TREE重新授权。局部无语义参数实例化按原定义域判断。共享发布许可必须明确写入相应任务批准对象及EVOLVE-01的manifest/base/action范围；普通基线批准不自动授予全库写入。

## 启动目标、三个对象和时点

在基线记录 `original_request_ref`、`goal_statement`、`non_goals` 与范围来源；“使用 ontology_modeling”只选择工作方式，不能把“审查现有项目”改为“构建工作流系统”。未经确认的窄化范围或排除内容不能覆盖原目标。

protocol_baseline_ref 固定实际采用的规则发布清单与字节；subject_snapshot_ref 固定被审对象或明确的输入契约；业务 definition_refs/definition_artifact 定义当前工作实体。相同文件可以有多个明确用途，但每种判断独立取证。schema 版本、protocol_revision 与 asset revision 不强制相等。

派发前的准备包不是已进入 Plan 的节点任务。正式 Plan 仍要求 TASK/CAP/CONTROL/RESOURCE 的真实条件，draft 是产物状态，绝不豁免隔离、确认或写域准入。所需当前基线不可推迟到整树冻结，未知派发先查询，不盲目新建。

## 当前验收与未来产物分别绑定

modeling基线的`current_modeling_input_suite_ref`指向[通用建模入口](../../tests/modeling-entry/suite.md)的本地适用绑定及其固定摘要；父seed/原目标、参数域、义务映射、动作和工具在Plan固定。Do生成的`produced_node_scene_suite_refs`是被验收的产物，不得回写成为本次Plan的新oracle。适用增量在运行前明确；不适用分类不能撤销必需义务。

文件集合用[subject-snapshot](../../templates/subject-snapshot.md)逐成员固定，集合摘要是清单字节摘要，不是任取一成员哈希。`protocol_baseline`、项目`subject_snapshot`、业务`definition`与本次运行的`review_run`分别具名；兼任用途必须显式声明，不能把检查运行日志替代审查原项目。

基线、run→artifact、check→graph、transition→前驱是有向非循环引用，应实际计算摘要。self仅可用于允许的内联契约，由外层清单固定；当前补算只能证明当前字节，不能证明历史阶段已固定。发现历史缺失走RECOVERY-01完整性记录，不倒填基线。


<a id="contract-fixed-records"></a>
## CONTRACT-01 · 固定记录的字段投影

[按需字段索引](../contracts/record-shapes/index.md)中的投影是既有模板在“拟作为固定已完成记录核对”时的机械字段投影，不是新的业务权威或运行状态。索引按 templates 文件名定位，一次只读当前记录类型；只说明必需字段的类型/非空及有限枚举。完整模板字段名保持原 schema，不把 request-decision 简写成另一套 status/value，或把 archive 简写成 last_sequence。

`strings` 是去空白后非空字符串；`positive_integers` 不接受布尔值；`lists/mappings` 非空；`booleans` 接受 true 与 false；`references` 必须可解析到具名固定对象；`digests` 必须是实算 SHA-256，允许字符串或 algorithm/value 形式。未列出的模板字段不一律必填；叶 children=[]、首回执 previous_receipt_digest=null 合法。模板草稿可空，不能当成固定记录通过。本投影仅包含当前维护样例采用的记录种类/阶段；未覆盖项返回未检查，不可默认适用全协议。

冻结基线和完整四边核验还须使用同一 `(task_id,attempt,baseline_digest)`；摘要逐个正确不允许中途更换基线。身份先验证存在/类型，再比较；多个 null 相等不是匹配。外部结果分别记录字节、结构、关系、语义、宿主资格覆盖，未检查层绝不继承 pass。

<a id="contract-requirements-basis"></a>
## CONTRACT-01 · 验收依据与被审输入分离

必需场景来自固定 SCENE-01，必需节点/义务/案例来自已核验原目标、父 seed、当前 Plan 的规格和验收。检查入口独立固定其位置和摘要；不能从候选清单自行声明的 required 列表推导全部要求。整份候选及其检查清单同步缩水也必须被发现。授权依据的来源真实性需要实际确认和审查，文件摘要本身不认证它。

要求映射记录来源及明确适用时点。当前父局部建模的要求是本节点和直接 seed；全树冻结才要求全部已展开节点/三场景，不能用全树集合反向阻塞父局部交付。更换 basis 是新核验/必要时新基线，不准为迎合候选静默重生成。


<a id="contract-check-coverage"></a>
## CONTRACT-01 · 核验覆盖与结论

维护检查按既有条款返回适用范围、实现/profile版本、实际输入摘要、断言数、结果和诊断。只有确实执行且全部满足的断言才能标为pass；未实现为not_implemented、未执行为not_run、证据不足为unknown/blocked。必需项未核验时本次验收为incomplete，不能由issues为空推导完整通过。字段/关系子集通过不继承为语义、真实确认、Agent隔离或发布资格。

字段附件属于CONTRACT-01的机械投影，不复制或覆盖业务正文。模板定义可用字段，附件定义当前profile的必填/类型；二者须绑定同一协议版本。完成态profile不得套用于停止/失败记录后倒填批准边；当前profile不支持的记录形态应返回unsupported/incomplete，STATE-01原状态仍有效。


## 正式记录准入与历史不完整材料

固定Markdown记录必须具有闭合frontmatter、唯一键和匹配类型；容错解析只可用于诊断，不能消除原错误。未知schema或缺当前profile不能按“字段差不多”放行。说明文和自定义业务报告可作为具名附录，不替代task、run、确认、转换或审查记录；只改schema标签不补足必需语义。

核验显式选择草稿、固定记录、停止记录或历史材料；不将完成态必填条件强加合法建模中间态、叶节点或首回执。历史基准缺失时只固定当前收到的字节及缺口，按RECOVERY-01追加完整性观察；不得补算后伪称历史已冻结、填造任务身份或倒签确认。新尝试先查询旧宿主活动写者/未知请求，历史不明不能视为已结清。


## 维护引用与发布集合的检查边界

有限字段投影不等于完整引用解析。已提供的引用逐项检查实际文件/具名映射、固定摘要、目标类型和适用身份；无法支持的引用语义报告unsupported。草稿、合法首回执及停止/失败记录选择自己的profile，不能强加已归档成功的必需字段。

发布核验从独立选定的版本化规则注册表及必需分发集合出发，核对资产ID/ref/revision/role、支持文件、规范依赖与全部摘要。候选注册表和候选清单一起缩减仍不能改变外部要求；不得写死永久250项。未知发布版本需独立适用策略，不自动继承旧版通过。版本化维护策略属于独立验证附件，不是新增PDCA权威、签名或发布授权。

<a id="contract-professional-plan"></a>
## CONTRACT-01 · 从原问题形成可检验方案

在既有baseline正文完成，不另建审批或schema。将原请求/父seed整理为：谁或哪个系统在什么条件下遇到什么问题、当前做法与可观察代价、目标行为/不变量、非目标、事实与待证假设。性能写清操作、负载、指标/单位和比较条件；研究写清要回答的问题、来源版本及证据边界。已有答案直接引用，不重复盘问；没有商业目标的学习/开源任务不强加付费需求。保留用户原目标，不用自己的改写覆盖授权。

存在实质取舍时比较推荐方案与最小可行替代（可以是维持现状），写理由、代价、失败影响、回退可行性和重新评估的触发条件；唯一合理的机械修改说明依据即可，不凑方案/评分。缺少会改变范围、安全或验收的事实则指出具体缺项；不能编造测量或假定用户同意。讨论中的建议不替代CONFIRM-01。

由已固定要求选择当前适用的专业方法，按[方法导航](../../bootstrap/work-methods.md)将路径、风险和判据写入原required_actions、constraints、testable_signal及suite正文。检查方向不是额外Agent或节点，不按文件数/变更行数豁免高风险检查；不适用须有依据，不能删已确认义务。方法发现新要求时按原冻结/REWORK边界处理，不在Check扩大基线。
