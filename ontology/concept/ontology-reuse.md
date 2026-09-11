---
schema: pdca.asset/v2
id: ontology:concept/ontology-reuse
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 复用优先的建模决策、固定定义与局部扩展
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
  - ontology:concept/work-node-contract
  - ontology:process/work-scenarios
  - ontology:concept/ontology-asset
  - ontology:concept/task-unit-test
  - ontology:concept/task-decomposition
reuse_spec:
  decisions:
  - reuse
  - local_extension
  - revise_shared
  - create
  modeling_search_required: true
  preserve_per_node_pdca: true
  definition_binding_kinds:
  - published_release
  - baseline_snapshot
  floating_runtime_refs: false
  unconditional_required_exclusion: false
---

# 复用优先的建模与局部扩展

## REUSE-01：先检查已有定义，再决定如何建模

`ontology_modeling` 的每个目标节点都必须执行本协议；不是可选参考技巧。`ontology_modelin` 等拼写不得作为新scene，规范值仍为 `ontology_modeling`。输入为当前用户目标/父seed、授权知识库范围、当前协议、通用建模suite与上下文预算。先检索不等于必须找到可用定义；目标库不可读时记检索失败，不能伪称“没有已有定义”。不得为了凑新增知识复制近义节点。

目标树归属、知识身份和任务身份分离。多个work/tree/node可以采用同一固定定义；同一类可在一树出现多次。引用不增加组成父，不能共用node_id所代表的出现位置、Agent、确认、run或完成回执。每个真实目标节点仍按SCENE-01完整PDCA；“复用”交付的是本次适用性、局部映射与测试，不是重抄原文。

## Plan中的候选检索与决定

1. 从实体职责、父要求、接口类型/单位、状态、副作用、边界与失败行为形成检索问题。先查授权目录/索引及别名，再按语义读取候选。记录查询、范围、可达库/版本、实际读取项、停止依据与未覆盖范围；名称/相似度只用于定位。
2. 按ONTOLOGY-01核对authority、采用限制、逐主张来源、版本和适用条件；按ADOPT-01检查已知错误公告。未核验或quarantined可作研究对象，不成为已接受约束或oracle。用户要求的规定性约束与外部事实分开取证。
3. 把父/用户必须要求逐项映射为已覆盖、需局部补充、冲突或未知。候选的无条件必需约束不得因任务不便而排除；条件约束须有明确适用性判断。选一小段说明不等于继承整个实体的类型保证。矛盾或未知影响必需要求时阻断，不拼出自相矛盾的“满足”。
4. 用下表为当前节点记录一个主要decision，多个definition_refs分别说明采用理由。原定义已完全满足时仍形成当前节点、参数/接口映射与三场景suite。Plan只固定检索结果、决定和建模验收；Do才生成最终节点与候选内容。决策改变且影响契约时重新确认，Check后不得改回Do。
5. 实际检索完毕且有可核查的不采用理由才能create。搜索范围不完整必须声明，不能宣称全世界不存在同类知识。新ID分配还要经EVOLVE-01命名空间检查。通过建模任务不自动发布共享知识。

| decision | 使用条件 | 必需产物/禁止事项 |
|---|---|---|
| reuse | 已有定义在当前范围满足要求，只有实例参数或接口映射 | 固定引用、采用/适用性记录、当前节点与suite；不强制新增知识 |
| local_extension | 保留已有适用义务，同时增加当前树特有约束、组合或细化 | 固定base与具名本地delta；不改共享字节，不扩大对外类型承诺 |
| revise_shared | 同一知识身份存在可复用补充/错误修正 | EVOLVE-01候选；当前工作只能使用已独立审查并确认的本地材料或等待发布，不把候选当全局权威 |
| create | 没有适用定义，或语义身份已经不同 | 检索及不复用理由、独立定义/约束/案例；禁止只换名字复制已有定义 |

当前树参数值（容量、部署位置等）在已有参数域内属于reuse+instance_parameters，不自动改变共享本体。新类仅在真实类特化时用specializes；特定目标节点不是凭写一个父类ID就获得全部可替换性。

## definition_refs 的唯一形状

每项是固定定义契约，不是路径字符串。必需字段：`library_id`（授权命名空间）、`definition_id`、`revision`、`content_ref`、`content_digest`（算法与真实字节摘要）、`manifest_ref/manifest_digest`、`binding_kind`、`applicability`、`constraint_bindings`、`excluded_constraints`、`claim_review_refs`、`adoption_id`。同一库的同ID/revision只对应一组不可变字节；内容相同的只读副本仍是同一版本，不成为第二权威。

`binding_kind` 为 `published_release` 或 `baseline_snapshot`。已发布版本的manifest按EVOLVE-01；旧库无发布回执时可用已授权基线快照，不伪造曾发布的事件，且仍须通过事实/适用性审查。`baseline_snapshot`不是让未核验候选绕过采用门禁：用途、来源、适用约束和确认必须完整。协议规则、定义依赖、共享术语与案例预期的实际传递闭包均需版本固定；重复依赖去重，闭包环可表示但不能无限读取，清单不引用自身摘要。

`constraint_bindings` 每项含source_constraint_id、local_constraint_id、applies、required、source_ref及test_case_refs。每个适用必需约束都要被采用；未采用项记录理由、条件判定和证据，不能把失败要求改成不适用。若来源没有稳定约束ID，记录固定字节内anchor/claim_id映射，不能在另一版本沿用不稳定行号。局部node中的最终有效约束与suite均固定摘要，不使用“最后读到的覆盖前者”。

runtime不得解析浮动latest、main或会变内容的URL作为固定定义。content_ref只有易变路径时先保留任务/工作级不可变快照；不存在或摘要不符则阻断，不自动找新版本代替。检索可看最新目录，执行只读已固定版本。库命名空间由真实来源或授权配置给定，不按内容相似度合并不同私有库的身份；未授权跨库复制禁止。

## 局部扩展不是任意覆写

本地delta包含delta_id、scope(work/tree/node)、base_refs、instance_parameters、新约束、接口变化、组合变化、案例增量和compatibility理由。优先保持base不动并在当前目标记录差异。有效契约=适用base义务+父/用户要求+经确认本地义务；有冲突则不能freeze。

增加更强的内部约束可以是本地细化，但缩窄对外允许输入/扩大错误集合/取消base必需保证是行为变化，不能宣称完整替代原接口。应明确新接口或显式适配边界与新契约，必要时create不同定义。纯参数选择在base允许域内无需共享修订；域外参数不能伪装为实例化。

新增任何强制要求、允许行为、单位、错误优先级、状态/副作用限制或oracle变化，必须归类为行为变化而非“只是扩展细节”。冻结树发生此类变化按TREE-01新树版本。无语义变化的文字修订也产生新内容版本，但旧树不被迫改引用、不继承新文件字节。

## 完成与失败

建模Check验证检索和决定、必要覆盖、适用事实、局部冲突及三场景正反例，输出 `reuse-decision`、固定NODE产物和ADOPT采用记录；Act可confirm_existing/no_new_knowledge/local candidate处置。共享候选待发布不应反向阻塞一个满足本地合同的节点；若本地必需事实尚无独立依据则仍阻断，不用“候选”放宽标准。

同一库中一份定义被两树采用，只共享知识输入，不共享运行结论。旧案例规范可以引用，当前run必须使用当前task/实现/环境执行；旧回执只作历史证据，不迁移为新PASS。详细测试与返工见[复用回归](../../tests/reuse-regression/README.md)及[双树示例](../../examples/ontology-reuse/README.md)。

## 入库去向与工作知识义务

实例动作与知识动作分别记录：`instance_action=create_occurrence` 只表示新的 work/node；`decision` 仍为 reuse/local_extension/revise_shared/create。检索对象是授权 ontology 中的实体、方法或组合定义；records 中没有历史工作既不证明无定义，也不支持复制已有定义换名。协议基线与被审对象按 NODE-01 单列，不用它们替代业务语义匹配。

每个决定有 `knowledge_disposition`：reuse 可以为 `existing_reuse`（无需新建发布）；其余按下表记录。参数在既有域内不生成新知识文件。

| disposition | 适用条件与记录 | 不能声称 |
|---|---|---|
| local_only | 一次性参数/本地差异/受授权范围限制的定义；reason 与用户范围来源明确 | 已沉淀共享定义 |
| shared_required | 用户/工作明确要求的可复用定义发布；obligation_id、目标 library/ID、范围、owner_node、后续任务或维护工作、完成证据条件必填 | 只有 records 候选就已经完成知识交付 |
| shared_deferred | 有共享价值但本轮仅交付候选；延期理由、责任/接续触发、未完成状态及授权依据必填 | 无期限“以后处理”或未获授权取消 shared_required |

项目私有本体库也是共享库；可复用不等于公开或必须跨企业通用。用户明确要求建设可复用本体库时，可复用新定义默认列入 shared_required（在 Plan 中确认），不能自动全设 local_only；复用现有合格定义可以满足相应知识义务，不强迫每节点新文件。需要改变原 shared_required，必须真实范围变更，不由 Agent 为归档自行改成 deferred。

工作索引分别保存本地节点覆盖与 `knowledge_obligations`。节点可按自身完整 PDCA 交付候选且正常结束；工作不能宣称“本体库已构建完成”，直到所有必需义务有 EVOLVE-01 精确发布/验证依据、当前采用资格有效，或经真实授权明确范围变更。缺发布权限不生成假回执；提出可归属目标节点的接续任务，不激活旧 Agent 或造无节点发布业务任务。

共享 payload 包含实体职责、边界、接口、组合角色、必需约束和可复用 suite/oracle；不包含当前 work_id/task_id/agent/conversation、未授权机器路径或本次 actual/PASS 作为实体语义。来源可指向任务，但理解必需语义与固定测试不能依赖新采用者无权读取的旧会话。入库按 EVOLVE-01 版本/授权/独立审查，不直接移动整个 records 目录。

建模在决定后按 DECOMP-01 评估当前实体与被复用组合模式是否需要继续展开。每个真实组成节点保留独立任务；共享定义可以由多个兄弟只读采用，不能以“规范被兄弟拥有”为由省略自身必需输入。
