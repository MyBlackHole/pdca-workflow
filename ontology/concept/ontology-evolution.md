---
schema: pdca.asset/v2
id: ontology:concept/ontology-evolution
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 共享本体候选、不可变发布与并发修订
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/ontology-creation-gate
  - ontology:concept/resource-ownership
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/task-rework
evolution_spec:
  immutable_version_key:
  - library_id
  - definition_id
  - revision
  change_classes:
  - editorial
  - diagnostic_coverage
  - behavioral
  - identity_change
  compare_base_required: true
  compare_catalog_required: true
  independent_review_required: true
  implicit_tree_upgrade: false
  publication_state_is_evidence: false
---

# 共享本体版本演进与发布

## EVOLVE-01：一份语义身份，多份不可变历史版本

本协议只管理共享定义的create/revise，不管理目标树组成或取代TASK-01。知识库逻辑键为(library_id, definition_id, revision)，每个键固定content_digest及依赖闭包manifest。`ontology/<type>/<slug>.md`只保留当前可发现投影，同一ID只出现一次；历史版本保存于授权知识库的`versions/<asset-key>/<revision>/`或Git固定commit/任务快照，不能放回ontology目录伪造多个活动ID。asset-key由目录映射到真实ID，不能直接把包含路径分隔符的ID当安全路径。

版本号是标识而非自动兼容证明；同一键不允许换字节，也不使用文件mtime决定新旧。目录有自己的单调generation和previous_catalog_digest，发布回执固定新旧head。多个库互相共享只在授权的namespace、版本和来源相同时是副本；内容相似不是身份相同，跨库同步并非本项目自带能力。

## 候选及变更分类

1. 由具名节点的ontology_modeling任务产生候选，保持task/work/tree/node/attempt、真实来源、REUSE-01检索与决定。候选记录`base_revision/base_digest/base_manifest_digest`（新建则expected_absent）、候选内容与manifest摘要、change_set、影响约束/接口/测试、兼容性证据、候选版本和授权作用域。
2. 每项变更归类 `editorial / diagnostic_coverage / behavioral / identity_change`。editorial必须说明为何允许输入/输出/错误/状态/单位/oracle/适用域未变化；diagnostic_coverage只揭示旧契约已禁止的行为，不能悄悄改预期；behavioral增加/删除/改变强制行为；identity_change原则上新ID并说明替代/分歧，不能换一个完全不同实体却继承原身份。
3. 分类为候选判断而不是自证。检查所有差异而非按文件行数或“补充细节”命名，未知兼容性记unknown，阻断自动迁移。重用原case_id且预期改变必须新case_revision；完整旧版本保留。
4. 候选wrapper保持`state: candidate`。待审payload可以包含预计发布后的active元数据，字节必须在审查前确定；它位于candidates/staging且无发布回执，不是可直接采用的活动权威。也可采用status:candidate的原稿后另产最终payload，但最终payload必须重新摘要并受审，不能在批准后改status/revision导致批准对象漂移。

## 当前工作交付和共享发布分离

当前节点可以交付独立核验/确认的局部NODE定义并将通用变化留为candidate_only；不要求等待共享发布或所有其他树迁移。未证实事实不能这样转正。共享修订若不在当前任务授权范围，先交付候选；后续实质审查/修订属于已明确的知识维护树节点、新Agent完整PDCA，不创建无节点的隐形业务任务。发布事件仅是宿主的写入/索引职责，不是父Agent审批。

## 审查与授权

`ontology-creation-gate`负责内容审查：父/用户要求、独立来源、类型语义、继承/引用闭包、兼容性、旧新正反例、错误定义控制与实际采用影响。来源/行为不足保持未核验，不因发布就把claim_status改成已证实。候选作者自检不等于独立发布审查；审查者身份/任务与作者分开，范围匹配当前payload/manifest。

发布授权必须能回链真实用户/库管理者对“向指定library/definition发布这个manifest、基于这个base”的明确同意。可复用CONFIRM-01的当前任务Check确认：其冻结结论包需**显式包含**上述发布动作、范围、manifest/base摘要与审查回执；普通“认可任务判定”不能推断为共享发布许可。不新增隐式确认类型，不复用另一task/树的批准。授权/审查保存在独立记录，manifest不引用未来response/receipt，避免摘要自引用。

## 最小发布顺序和并发冲突

1. 固定最终payload和依赖闭包manifest；manifest包括library/definition/revision、payload位置/digest、适用限制、依赖/术语/案例的精确版本。不含自身digest或未来批准。真实读取闭包计算摘要；不可访问、不同ID同版本内容冲突或适用必需约束缺失时停止。
2. 独立审查并取得当前对象/动作的真实授权。建立proposal_id，取得RESOURCE-01共享知识发布资源所有权；授权不能代替锁。库级单写者或宿主比较提交保护目录，定义级expected_base仍必须检查。
3. 在提交边界比较当前catalog generation/digest、当前head和候选base_revision/base_digest/base_manifest_digest。任何不一致都停止自动提交。不同定义引起的generation更新可以刷新目录检查后重试，但同一定义head已变化必须rebase/merge；禁止“串行执行所以最后写入获胜”。
4. 新建必须检查目标ID和版本key确实未发布；已有相同key相同字节且同proposal回执时返回已有结果，不重新宣称独立发布；同key不同字节拒绝。新ID仍需语义去重审查，不能仅依据目录空位。
5. 固定版本字节先入不可变store并重读核验；宿主在同一可信提交边界使“发布提交记录”和head更新可一致恢复。无跨文件事务的最小方案是单写者追加完整提交记录为唯一权威，head/当前ontology文件为可重建视图；读者只消费完整无冲突提交记录。不声明两个文件rename构成跨文件原子事务。需要更强保证而宿主不具备则阻断。
6. 发布回执含proposal、发布manifest、base、审查/授权来源、提交前后generation和真实后端回执；独立保存不修改已批准字节。失败部分不能当成功；恢复核对实际提交记录和版本store，不重复副作用或盲目提升head。投影视图不匹配时读者使用manifest固定字节或阻断，不把半更新视图当发布事实。
7. 发ADOPT-01知识事件/影响通知，更新本库采用索引视图。新head只用于后续检索，不自动重写任何既有目标树、确认或suite。

## 过期候选的返工

A/B同基于r1，A先发布r2，B即使资源锁随后可得也不能覆盖r2。保留B原失败提交→获取r2→三方比较r1/r2/B→按语义处理相同约束、接口和case冲突→新candidate_revision、新payload/manifest→重新分类、全必需回归、独立审查与当前授权→以r2为base发布。即使文本diff没有冲突，语义冲突也不能自动合并。

两个候选相同内容也必须核对实际身份/回执，不共用作者task或生成假的第二次工作通过。重新整理候选属于Do内未改合同且预算可用的有限修复；Check后或改变验收/范围必须按REWORK-01新attempt和新Agent。取消/超时按CONTROL-01处理，不绕过Check或写权撤销。

## 冻结引用、已知错误与版本采用

旧树仍读取原版本。普通新版本发布不使所有旧树自动stale，也不能直接把旧PASS搬到新版本；明确升级需要ADOPT-01影响判断与TREE-01新版本。已确认严重错误通过独立advisory限制旧版本采用/发布，不修改历史字节。保留版本和撤销可信性是两件事。

历史定义资料缺发布回执时，按REUSE-01 baseline_snapshot导入且写明来源，不能补造历史发布。当前代码/文件维护升级也不是一次已在真实Agent上完成的本体任务，不在本项目填造生产catalog或授权。模板：[候选](../../templates/ontology-revision.md)、[发布清单](../../templates/ontology-release.md)、[提交回执](../../templates/ontology-publication.md)、[目录](../../templates/knowledge-catalog.md)。

## 必需知识发布与局部完成的边界

REUSE-01 的 knowledge_disposition/obligation 是本次工作的知识交付责任。本地候选仍可结束本节点完整 PDCA；但 shared_required 未满足时，工作级 knowledge_goal_satisfied 不能为真，candidate_only 只记录事实而非豁免。发布责任必须是已声明工作/维护树中的具名节点及真实授权接续，不增加父 Agent 持续审批。

入库验收检查独立可读的定义 payload、相应 suite/case/oracle、授权可访问的来源及精确版本闭包。纯任务草稿、记录路径列表和本次 PASS 不是可复用实体。既有 definition_ref 足够时不生成重复 payload。工作级义务引用计划目标及完成条件，实际 publication 作为外部追加履行事件，不能回填冻结 NODE 或基线。

共享组合定义优先引用稳定角色契约与适用条件；工作树绑定具体 child occurrence。父早期定义不能依赖未来孩子版本而阻塞自己的建模。最终发布若包含具体孩子版本，须另固定完整最终 payload 并完成独立审查、授权和 base/catalog 比较；这不是把未来字节塞回早期已确认文件。发布物中不得把角色引用当第二组成父；新树采用模式必须展开所有适用必需角色并逐节点执行。

本项目维护交付到 ontology 的文件属于仓库资产快照，不自动生成真实 ontology-publication/catalog/Agent/用户回执。首次部署可按 baseline_snapshot 核验使用；要求在线共享发布事实时必须实际完成 EVOLVE-01，不能把打包说明当授权。
