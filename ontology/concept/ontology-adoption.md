---
schema: pdca.asset/v2
id: ontology:concept/ontology-adoption
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 跨树采用清单、影响分析与显式迁移
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/work-ontology-tree
  - ontology:concept/task-rework
  - ontology:concept/task-control
  - ontology:concept/ontology-asset
adoption_spec:
  identity_fields:
  - library_id
  - definition_id
  - revision
  - work_id
  - tree_revision
  - node_id
  runtime_status_separate_from_content: true
  index_single_writer: true
  incomplete_index_means_no_users: false
  reuse_completion_receipts: false
  unchanged_pinned_version_automatic_stale: false
---

# 跨工作树采用、影响与迁移

## ADOPT-01：共享定义，独立承担本次采用责任

每个采用行归属于(library_id,definition_id,revision,work_id,tree_revision,node_id)并有稳定adoption_id。不可变行保存content/manifest摘要、采用约束、逐主张审查、local delta、suite/case映射、scope/权限、产生该行的modeling任务和基线。后续scene任务及运行证据以追加观察关联，不让采用行反向引用未来task或使原基线摘要改变。

采用事件为proposed/accepted/superseded/affected/cleared等记录，状态视图可重建；它们不是PDCA新phase，也不能授予运行写权。提议、确认冻结、执行前、独立审查与发布前均核对当前已授权知识公告视图与采用范围。基线保证输入不变；公告视图允许新发现安全/正确性问题阻断继续使用，不偷偷改变原要求。

## 责任与存放

节点Agent生成自己的固定adoption行/事件建议，不并发写全库索引。宿主知识库索引单写者按RESOURCE-01和实际来源合并到授权`records/knowledge/<library-id>/adoptions/`；也可使用授权外部库，接口能力必须真实。工作tree冻结清单包含所有采用行及定义闭包的固定引用，不包含将来事件。

采用索引事件最小字段为event_id、adoption_id、kind、origin_source_ref、固定采用行摘要、work/tree/node、previous_event_digest、observed_index_generation、actor_ref和event_evidence_refs。accepted要求对应当前已确认冻结对象及真实来源；superseded只替换工作视图而不覆盖旧行；affected需问题/公告依据；cleared需本声明范围的回归/不受影响证明，不能只看新head存在。事件由唯一索引写入者按实际提交顺序追加；未知结果先核对真实事件，不按Agent自填时间或重复投递覆写。无原子比较能力仅声明可信单写者的实际保证，不能从字段推导CAS。

共享库索引记录catalog/view generation、扫描/事件覆盖范围、可访问工作清单和缺失区域。跨主机未配置同步时，只能说已覆盖可访问注册采用者；“查无记录”不证明无人采用。索引缺失可由已授权冻结基线重建，但未完成时标coverage_incomplete，不得宣称全库影响已清零。授权不允许的私有树只保留可公开的标识/影响通知，不复制其内容或用户消息。

本轮交付不生成生产adoption或catalog样本成功记录。示例固定在examples并标fixture；模板的null/空列表不构成采用成功。

## 更新并不等于自动迁移

新版本发布后，对已登记采用者按definition实际闭包和constraint映射计算候选影响：

| 情况 | 应采取的动作 |
|---|---|
| 仅有更晚版本，无旧版缺陷且当前树不采用新版 | 保持当前固定版本，记录可选升级；不把旧证据自动改为stale |
| 树明确请求采用新revision或新的local delta | 在新树版本重新建立定义/套件/依赖基线并真实确认；三个场景逐节点覆盖，未变内容只作输入 |
| 新诊断用例揭示既有契约违例，语义不变 | 保留旧套件与失败，固定新诊断及suite；按TEST/REWORK在相应新attempt回归，不以此暗改冻结期望 |
| 已确认当前采用约束/闭包存在错误或不满足适用域 | 发布可信advisory；受影响运行先安全停止相关动作/阻断采用与发布，按CONTROL与REWORK处理；历史字节/结果不改写 |
| 更改只是其他作用域的可选条目 | 明确non_affected理由和证据，不假设全部旧任务都需要重跑 |
| 采用索引不完整或关键主张影响未知 | 标unknown与范围缺口；关键采用/发布fail-closed，不以空列表宣布无影响 |

revision号相邻、diff很小、相同名称和共同模型自评，都不是兼容性证明。知识依赖闭包变化也属于变化，不能只比较顶层定义文件。local delta需重新相对于新base检查；升级删掉base保证不能靠旧delta掩盖。

## 影响闭包的正确范围

先找引用相关定义revision/受影响约束及其语义依赖闭包的adoption。再在每棵受影响工作内沿实际产物依赖和组成祖先展开到实现/组合/审查/发布证据。`relates_to`不传播“必然受影响”；无法判定必需事实的影响时保守标unknown并复核，而非一律删除所有引用或自动放行。

修复某个孩子不要求其等待祖先才交付：本地完整PDCA与本地必需回归完成后可交付，工作issue仍开放；父/根各自完整PDCA，再独立复审。全局知识问题可保留“在库定义已修复、尚有采用者未迁移”两个状态；某一工作通过不等于所有工作都已修复。

## 安全公告与旧版本

advisory必须有notice_id、发行者/真实来源、受影响library/definition/revision或摘要、claim/constraint、严重性/依据、建议动作、发行顺序和撤销/替代依据。公告是运行可信性控制记录，不放进已批准定义字节中。未知来源不能修改已确认目标；有可信错误证据但影响待定时先阻断相关危险操作并调查，不捏造确定性。

新采用、Plan→Do、恢复以及整树发布前核对当前授权notice视图。宿主通知丢失/离线时按基线约定的新鲜度与风险策略处理；没有可信时钟/事件不能声称已同步全部撤销。公告到达与发布竞争必须在真实宿主的有效控制边界重新检查generation/停止状态；没有此能力而任务要求硬保证时阻断。正常无错误的新版本通知不能用作取消全部旧工作。

## 升级与返工

迁移记录列出old/new definition+closure、old/new tree、constraint/case映射、局部差异、影响节点、确认对象、后继任务、回归证据和仍未覆盖的采用者。只修改实现且合同不变按旧树新attempt；采用定义/接口/允许行为/期望变化按TREE-01新树版本。对未变节点仍执行所需覆盖核对，不复制旧PASS/确认/Agent。

关闭影响事项需要每个声明完成的采用者有新固定对象和真实验证，或有可核验的不受影响理由。退役/取消工作可完成行政处置，但不标其实现已经修复。清单coverage_incomplete时可关闭明确单个工作问题，不能关闭“所有采用者已处理”的全局主张。

## 完成判据与资料重用

建模本地完成只要求自己的采用行完整、有效、与NODE/suite一致；跨树全量登记/迁移不反向阻塞本地任务。宿主接受节点交付时建立可恢复事件索引；新的实现和发布在采用/公告检查失败时阻断。已有claim-review仅能作为输入复核其来源、版本、范围和权限，不能把旧任务的authorizing user或PASS当本任务授权。

模板：[采用行](../../templates/ontology-adoption.md)、[影响处置](../../templates/ontology-impact.md)、[公告](../../templates/ontology-advisory.md)。高层流程仍由SCENE-01负责，知识索引不是另一个常驻控制父Agent。

## 协议基线复用与知识义务观察

共用的流程规范由工作级 protocol_baseline_ref 固定，任务按需加载并检查适用性；不要求每个节点为同一协议重复一份业务 ontology-adoption。业务 definition_refs 仍逐节点登记采用责任。协议若同时是审查对象，必须另有 subject_snapshot_ref，不继承“已经加载就是已经审查”的结论。

knowledge_obligation 的履行事件含 obligation_id、origin_work/tree/node、固定候选或已有定义、实际 release/publication 摘要、权限与范围、独立核验及当前公告视图。索引单写者汇总；声明 shared_required 的工作只有在自己范围内全部必需义务满足时才能声称知识目标完成。新发布不能回写旧基线；不同树不共用运行回执。只读定义多节点采用是合法共享，不作写入冲突处理。
