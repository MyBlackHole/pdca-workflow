---
schema: pdca.asset/v2
id: ontology:concept/work-node-contract
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.1
summary: 节点契约：实体、组合和单元测试
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/task-unit-test
  - ontology:concept/task-test-case
  - ontology:concept/pdca-execution-contract
  - ontology:concept/work-dependency-graph
  - ontology:concept/resource-ownership
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# 节点契约：实体、组合和单元测试

## NODE-01：每个目标节点的最小语义

节点使用 `pdca.work-node/v3.4`（运行目标实例，不是知识库 asset 的替代模式）。必须明确 work_id/tree_revision/node_id/node_revision、parent_node_id、children、definition_refs、目标、in_scope/out_of_scope、接口、约束、验收、测试集和交付。

| 契约项 | 必需内容 | 失败信号 |
|---|---|---|
| entity | 当前实体的职责、允许行为、排除项和可观察边界 | 只有“实现模块”或把多孩子全部业务塞给叶子 |
| requirements | 稳定 requirement_id、来源用户/父 seed、必须性、负责者 | 父目标遗漏；同一义务重复实现导致冲突 |
| interfaces | 名称、类型、单位、版本、输入前置、输出后置、错误、状态与副作用 | 字节/条数等单位不一致；错误传播未定义 |
| constraints | 稳定 constraint_id、允许/禁止、继承来源、判定 oracle | 无法给出失败反例，或实现者可任意解释 |
| composition | 直接孩子端口映射、数据/控制顺序、组合不变量、故障传播 | 所有孩子通过便宣布父通过，没有真实组合测试 |
| test_suites | 三场景各自 suite_ref/revision/digest、约束覆盖、正反例与判定 | 只给两个文字例子；空集/全跳过 |
| deliverable | 具名固定产物、接口版本、资源所有权与可导入位置 | 仅写任务归档，无法给父节点使用 |
| context_budget | 必读定义/约束、按需证据指针、复杂度上限与拆分理由 | 根需要读取整树后代对话才能集成 |

每条必须约束必须映射至少一个合法行为正例、一个违反该约束/错误实现反例及适用的边界案例；确实不适用的分类需语义理由和真实审核，不能以“不易测”豁免必须约束。更多覆盖规则见 TEST-01/CASE-01。

## 叶节点与组合节点

叶节点：children 为空，单一职责、可独立验证；其 suite 直接检验该实体。内部节点与根：children 非空，必须有自己的 composition、产物和组合测试；不能只汇总孩子 PASS。模拟孩子可用于早期诊断，但最终组合测试必须使用冻结版本的真实孩子交付物。

本体定义不天然正确。建模测试核对是否忠实于父 seed/用户目标、是否自洽、正反例能否区分预期行为；执行测试检验实现；审查测试检验实际对应和审查漏报/误报。

## 冻结粒度

节点定义、接口、必需约束和三个 suite 的规范与案例在树冻结时固定；平台测试绑定在各场景任务 Plan 中固定，不能改变期望语义。执行发现新故障可增加诊断/回归案例，但不得删除必需案例、把必需改成可选、修改 oracle 来迎合结果；需要改规范走新树版本。

相关模板：[目标节点](../../templates/work-node.md)、[套件](../../templates/test-suite.md)、[案例](../../templates/test-case.md)。


每条从reference导入的事实须有claim-review与适用范围；来源不足不能用同一模型生成的正反例自证。已知错误/隔离资料不得进入定义或suite oracle。目标规范来自用户确认，技术事实来自独立核验；二者权威来源分开。


实际输入在dependencies按DEPENDENCY-01声明producer node/scene/artifact、consumer及来源义务，不能以relates_to代替。资源声明包含规范化范围和side_effects，不只写一个本地目录字符串；RESOURCE-01负责真实预约。模板是草稿，空dependencies不能被解释为实际运行图已完成检查。

## 固定引用和有效契约

新目标节点使用pdca.work-node/v3.4；definition_refs逐项形状、约束覆盖、局部delta与兼容性由REUSE-01唯一规定。modeling_decision_ref绑定本节点决策，definition_manifest_refs固定实际语义闭包；effective_contract_ref/digest绑定合成后的当前节点义务；adoption_refs记录已采用定义。

共享定义引用不是第二组成父，也不是任务替身。已有定义完全满足时可不新增知识，但本节点仍有自己的接口映射、三场景suite及完整PDCA。局部细化不允许删除父/基准必需保证；事实缺证不能靠自己生成反例变真。候选共享发布不是本地合格交付的前置。

## 建模双产物与引用用途

每个节点交付 `definition_artifact` 与 `work_instance` 两个逻辑产物，不强制重复两份正文。已有定义适用时，固定引用及差异就是定义产物；新语义才产生独立 `pdca.asset/v2` payload。工作节点保存当前对象绑定、参数、局部 delta、组成位置与测试工具映射。独立定义必须描述跨三个场景都成立的实体职责，而不只是“允许创建这些 records 文件”。当前 modeling 任务可以只设计，不能把实体实际执行/审查职责全部排除掉。

| 引用字段 | 用途 | 固定时点与不可替代项 |
|---|---|---|
| protocol_baseline_ref | 指导任务的规则与版本闭包 | 派发前固定；不逐节点复制所有流程规则为业务本体 |
| subject_snapshot_ref | 实际被审/被实现对象 | 当前已知输入 Plan 固定；模型阶段可先定义目标输入契约，真实对象在对应执行 Plan 固定；不能声称六个规则摘要就是全库快照 |
| definition_refs / definition_artifact | 当前业务实体语义及采用、局部差异 | 已有输入在 Plan 固定；新产物在 Do 后固定；不得用自己的产物反向生成 Plan oracle |

同一文件承担指导规则与被审对象两种用途时分别标记，不能因为已作为规则加载就认为审查完成。必需业务语义不能只用大量流程规则 ID 冒充；定义可内联在固定有效契约（local_only），但 shared_required/shared_deferred 的可复用新定义必须提取为独立 payload，不能只给 task_id 或草稿路径。

## 递归评估与入库处置

`decomposition` 按 DECOMP-01 保存 leaf/composite/blocked、覆盖、工作量/预算/进展、直接 seed 和证据。默认 seed 可继续评估，不固定孩子数或最大层数为业务验收。共享只读知识不属于唯一“拥有者”。

`knowledge_obligations` 按 REUSE-01 记录已有定义采用或新定义的 local_only/shared_required/shared_deferred；同一 `knowledge_obligations` 按ID同步到宿主工作清单，不再另存同义义务字段。节点本地完成与共享发布完成分开：本地可交付而工作知识义务仍 open，但不能以 candidate_only 抹除已确认必需发布项。引用有效现有发布或授权快照的 reuse 不需要再制造新发布。

## 分时点完成条件

派发前准备不伪称正式建模。当前 modeling Plan→Do 前固定通用建模 suite/输入/真实绑定和确认；无需预知待生成节点。建模交付前，当前实体三个场景的必需案例、样本类别和 oracle 已确定；工具绑定和未来执行结果可未运行，但 suite 不得是 planned-not-yet-defined。父的后代定义尚未生成不妨碍本地 seed 交付；整树冻结时检查所有实际节点。

详细规范样本可从 [审查实体组合](../pattern/audit/project-review-composition.md) 定位，使用前按 REUSE-01 固定适用性。本版新增资产是仓库文件交付，不是已经在真实宿主发布的知识回执。

## 双产物的最小记录形状

work_instance就是当前work-node本身，不要求再复制一份。definition_artifact是一个具名对象：kind为reused/local_definition/shared_candidate；semantic_ref/digest固定业务定义或有效契约，base_definition_refs指向已采用固定基准（适用时），candidate_ref指向EVOLVE候选（仅shared_candidate）。reused允许直接引用一个已固定定义；多定义合成则semantic_ref固定合成后的有效契约。local_definition可指self，但digest由外部manifest固定，不在自己文件中保存自身摘要。

每种kind都必须能定位跨场景实体语义；只有task_id或records路径清单不合格。Plan中的definition_artifact_plan是生成意图，不伪称尚未存在payload已有摘要；Do后的definition_artifact才绑定真实字节。decomposition和knowledge_obligations位于当前实例/决定，不混进共享业务实体的运行字段。

## 必需约束的语义覆盖与本地输入

覆盖矩阵不能只验证case ID存在；每条必须约束须说明负样本实际违反它的哪个谓词，并定位输入差异。禁止递归的反例不能用“角色互相推诿”替代，知识共享反例不能留空。来源case按CASE-01绑定后才是本节点有效契约。

当前modeling任务采用通用入口的本地固定绑定；三场景生成物在`produced_node_scene_suite_refs`引用。复用来源的合成facts案例只能证明结构谓词；实体承诺从原材料提取和判断时，须另外固定原材料案例及输入→事实→证据→结论链。
