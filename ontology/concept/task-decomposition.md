---
schema: pdca.asset/v2
id: ontology:concept/task-decomposition
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.9
summary: 递归子本体判断：叶子是验收结论，不是父任务预设
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-node-contract
  - ontology:concept/work-tree-scheduling
  - ontology:concept/ontology-reuse
  - ontology:concept/task-unit-test
decomposition_spec:
  decisions:
  - leaf
  - composite
  - blocked
  seed_default: undecided
  every_modeling_node: true
  empty_children_is_proof: false
  progress_required: true
  coverage_owner_unique: true
  read_only_knowledge_shared: true
  case_is_automatic_node: false
---

# 递归建模与子本体分解

## DECOMP-01：每个节点重新判定，不能用结构自证

每个 `ontology_modeling` 节点，包括父任务交付的每个孩子，都在自己的完整 PDCA 中评估当前**实体全部职责**是否可独立建模、实施和审查。不是只评估“写本次草稿”需要多少文字。结果为 `leaf / composite / blocked`；草稿可为 undecided，合格交付不得为 undecided。`children=[]` 是结构事实，不是叶子证据。

该规则只决定目标实体的分解；单条约束、一次搜索、一个案例、一次工具调用不自动成为新目标。已经成为实际组成节点的对象仍必须逐场景、逐 attempt 完整 PDCA，不能为了少派 Agent 又合并回去。

## 输入与判断记录

在 NODE 的 `decomposition` 中集中记录，无需另建一份任务：

| 字段 | 必需语义 |
|---|---|
| decision / reason | leaf、composite 或 blocked；理由必须来自工作而非节点名称或目录深度 |
| obligation_coverage | 每项用户/父必需要求的主要交付负责人，或当前节点组合义务；可有多个验证参与者 |
| independent_parts | 潜在子实体的输入、独立输出、oracle、失败处置；不按一行一句机械拆任务 |
| workload_basis / context_plan | 实际对象清单与工作量依据，必需同时读取、可分批读取和外部索引；三场景分别评估 |
| budget / observability | 任务已授权的限制、计量依据、估计与实测区别；不得虚构模型上下文容量 |
| progress_measure | 拆分前后单节点最大负担、父组合负担和下降理由；没有进展不得继续包装同一目标 |
| child_seeds / composition_checks | composite 的直接子槽、边界、责任、接口和父组合测试；不引用尚不存在的后代回执 |
| stop_conditions / evidence_refs | 有限停止条件、未知项、评估证据；达到上限仍不可执行则 blocked，不强制判 leaf |

`leaf` 需要目标不缩水、没有遗漏的独立必需实体、具名产物、明确正反例/oracle，以及三个场景必要上下文与验证在当前方案内可控。大资料可按需检索、分批测试，不以文件总量一票否决；不可同时装入的必要约束也不能被悄悄省略。仅“叶无孩子”“已经拆过”“当前草稿很短”不构成理由。

`composite` 需要至少两个有真实分离价值的直接部分，或一个经具体理由证明减少负担的组成部分；只把原目标同义重述给唯一孩子不算进展。每个孩子仍独立评估，父的直接子数/接口汇聚必须可控。不能用无限层目录代替减少最大单任务负担。

`blocked` 保存未解决边界、能力、预算或事实与下一步；不发布可用定义，不按比例掩盖漏目标。模型夹具中的数字仅用于确定规则，不作为真实宿主容量。

## 父 seed 允许继续拆分

父建模任务固定自身定义与直接子 `role_id`、职责、输入输出、约束、交付边界及 `decomposition_policy: assess_recursively`。默认不写“孩子不得有孩子”。确需原子实体时用 `atomic_if_justified`，给出来源和可核验理由；孩子仍检查是否成立，反证时提交设计问题而非强行保持叶子。

孩子在 seed 允许边界内增加自己的直接孩子，不改变父已有直接子身份，也不反复唤醒已归档父 Agent。候选树索引由宿主将各节点固定交付装配；不让孩子修改父定义或全树索引。若要改变父接口、必需义务、允许域、资源责任，必须相关父节点新 modeling attempt；已冻结目标变动按 TREE-01 新树版本，旧确认不复用。

## 完整性、知识共享与组合

每项必需父要求有一个明确主要交付负责人（孩子或父组合），不得推给“以后使用方”；同一条要求可有多处验证。知识定义和流程规范是只读可共享输入，不因兄弟采用而被另一个节点排除。唯一组成父、主要交付责任、实际写权与知识引用是四件不同的事。

组合父的测试检查接口、单位、状态与错误传播，以及跨分片遗漏和矛盾；孩子各自 PASS 不推出父 PASS。复用组合模式时展开其适用必需角色，每个实例节点重新评估与完整执行；不能把已有子树折叠成黑箱省略任务。可选角色由固定条件决定，不因失败改成可选。

## 两阶段固定，不反向等待后代

父本地建模完成=自己的定义、角色契约、直接 seed、三场景测试语义已固定且本地建模测试真实通过；不等待尚未生成的后代产物。实现/审查 suite 可按固定角色接口表达输入，但其期望必须已经确定，实际工具和孩子版本由后续任务 Plan 固定。

全树冻结=所有实际节点建模交付可用，角色映射与最终节点/套件/图闭包固定。后代新增的语义若超出角色约定，不能由宿主“装配”替代新节点任务和相应审查。共享父定义应优先引用稳定角色契约；若最终发布要加入孩子精确版本，先构造新最终 payload，再独立审查/授权，不用早期 seed 确认批准未来字节。

## 验收与返工

至少实际提交一个可执行叶子正例、一个应拆分反例、一个不能再包装同义子任务的无进展反例，检验“永远判叶”和“永远拆分”的错误判定器。仅当前候选没有错误不算反例能力通过。固定失败样本→隔离复现→修改边界/候选→新版本完整本地回归→受影响孩子重新核对 seed；不得改旧成功回执或跳回 Do。详见 [K07—K12](../../tests/modeling-regression/README.md)。

## 累计上限不替代局部可执行性

拆分除最大单节点负担下降外，还核对REWORK-01工作累计预算、已消耗attempt和剩余完整回归成本。不能通过多开Agent、多包一层或重编号隐藏总成本。父只证明自己的定义/组合与直接seed可控，孩子是否最终为leaf由其自己的任务判断；预算不足保存证据并blocked，不强制叶化或删必需目标。

<a id="decomp-rejection-witness"></a>
## 拆分先给“可独立拒收”的见证

在已有 `decomposition.independent_parts / reason / progress_measure` 中回答：**能否在接受相邻部分的同时，有意义地拒收这个部分？** 给出其独立输入、交付、oracle及失败边界；不能只说“不同文件”“不同角色”或“方便并发”。这不是新增表单或父层批准。

| 观察 | 处理 |
|---|---|
| 测试、实现、配置、文档共同构成一个可验收能力 | 留在该节点内部步骤；各自被读取或执行不产生新实体 |
| 两个部分有各自可拒收产物，接口与失败责任明确 | 作为候选直接部分，仍评估父组合义务、三场景负担与累计预算 |
| 只能用“整件事尚未完成”解释任一部分失败 | 拆分见证不足；重新找边界，不以任务数增加证明进展 |
| 实际组成节点已经固定 | 不为了省成本合并消失；变更按 TREE-01 的新版本和原授权处理 |

例：为“输入解析器”建文件、实现边界检查、写测试通常是内部步骤；“编码器/解码器”若分别有独立接口与失败判据，可以是候选部分，往返兼容仍归父组合。例子不是强制树形模板，结论来自当前合同。

规划成本时，N个实际节点的首轮完整三场景对应3N个任务和6N个Plan/Check确认对象；不是6N次聊天，也不含返工、整树确认或发布。尚未生成后代时仅列当前已知数及估计范围，不为取得精确总数反向等待后代。资源或预算不足仍为blocked，不削弱四阶段或预设所有孩子为leaf。
