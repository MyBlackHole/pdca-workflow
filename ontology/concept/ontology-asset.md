---
schema: pdca.asset/v2
id: ontology:concept/ontology-asset
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.6
summary: 本体节点序列化与权威边界
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-rule-type-controlled
  - ontology:concept/ontology-rule-acyclic
  - ontology:concept/ontology-creation-gate
  - ontology:concept/knowledge-artifact
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
serialization_spec:
  schema: pdca.asset/v2
  semantic_kinds:
  - class
  - individual
  authorities:
  - normative
  - reference
  statuses:
  - active
  - candidate
  - deprecated
  - historical
  relation_keys:
  - specializes
  - instance_of
  - composed_of
  - part_of
  - requires
  - depends_on
  - configured_by
  - guides
  - relates_to
---

# 本体节点序列化与权威边界

## ONTOLOGY-01：一个节点一份身份

活动节点使用 `pdca.asset/v2` YAML frontmatter加Markdown正文。必需字段：schema、id（全局唯一）、type、semantic_kind、layer、status、authority、revision、summary、relations（根可为空）。同一文件只保留一份活动身份；旧标识放aliases，出处放source_ids/provenance，不保留第二段活动frontmatter。

`type` 是资料分组而非“类/实例”判断；它必须匹配ontology下第一个目录分组。允许嵌套目录，例如ontology/domain/pdca/xxx.md的type为domain，而不是pdca。受控词表由ontology-rule-type-controlled定义。

`semantic_kind` 为class或individual。specializes只能class→class，instance_of只能individual→class；不能反向派生二者。领域知识文档可作为KnowledgeArtifact实例，主题关联用relates_to，不能把“某主题的文章”当作“该主题的子类”。

## 权威等级

`authority: normative`定义工作协议；`reference`是领域/方法资料，采用前需检查适用性，不能改写生命周期。`status: active`才可纳入活动子图；candidate/deprecated/historical不作为当前规则。引用旧ID可以用于迁移定位，但必须沿replaced_by读取活动权威。

正文和frontmatter一致才可使用；同一属性的定义冲突不以“离得近”“写得晚”自动解决，报告并阻断相关动作。revision说明版本，真实内容摘要才固定字节。

## 关系词表

| 关系 | 语义/执行作用 |
|---|---|
| specializes | 类特化；继承父类适用约束；多父允许，继承环禁止 |
| instance_of | 具体实例属于类；不表达子类 |
| composed_of / part_of | 整体与部分，方向互逆；仅对本次目标涉及部分投影 |
| requires / depends_on | 必需依赖；投影为执行边前明确实际动作/产物 |
| configured_by | 由配置参数化，目标范围由领域约束决定，不全局写死TLS |
| guides | 知识指导某对象/过程；是候选线索，不自动派发任务 |
| relates_to | 弱相关，可互相引用，不继承、不自动加载/执行 |

关系值必须是ID列表。testable_signal是属性/验证描述，不属于relations。`domain`若使用也是已存在ID列表。不得用来源URL或task ID冒充本体节点边；它们用来源字段表达。

严格部分关系将part_of反转为composed_of方向后去重再查自包含；A composed_of B和B part_of A是同一事实，不是执行死锁。执行DAG、继承图、部分图分别检查，绝不对所有语义边并集施加无环要求。

## 属性与验证

属性可用name/desc/constraint/testable_signal表达；可测试信号须指明观测对象、判断方法和失败判据。关键词出现、引用次数和文件长度最多是结构信号，不能证明业务行为。规则创建和发布检查见ontology-creation-gate。

## 工作目标树不是知识图的可选投影

本资产模式用于可复用知识；某次工作按TREE-01使用唯一父归属的组成树，运行节点用pdca.work-node/v3.4。知识图的多继承/相关关系不构成工作第二父边。类定义被多次实例化有不同node_id；每个目标node按SCENE-01各有完整任务。


## 证据层级与资料采用（保留3.1边界）

属性`evidence_level`可为structure/source/semantic/behavior/unclassified。structure只证明格式、检索或测试发现；source要求固定一手来源与匹配版本；semantic核对命题和推导；behavior要求真实对象实际运行。一个层级的PASS不能提升另一层。旧grep/collect-only保留为structure，不删除定位价值，也不能用它们批准公式或行为。

reference节点的`validation.claim_status`为unverified/source_checked_scoped/quarantined；`validation.adoption`为claim_review_required或blocked。active只表示稳定节点可定位，不代表已证真。缺少新字段时按unverified+claim_review_required处理，不能按旧版本乐观通过。

- claim_review_required：采用前逐项记录claim_id、原文、适用版本/条件、独立来源与位置、已核验范围、缺口、关联约束和测试。source_checked_scoped仅覆盖checked_claims，不为整篇或真实运行背书。
- blocked：当前节点只可作为待审对象/检索线索，不能作为实现合同、继承约束或test oracle。即便存在引用边也不得自动展开为义务。需要其必需事实的任务停止或取得独立证据重建新版本，不能静默删除要求。
- 图的相关边不是错误传播证明。修复后检查实际采用记录与直接/传递依赖；未核验引用者不自动变成已修复。当前包没有生产采用记录，不能补造“所有受影响任务已回归”。

修改元规则的依据可以是已确认用户设计，不要求外部论文；外部技术事实必须核对一手版本；经验推断明确不确定性。模板见[主张审查](../../templates/claim-review.md)。

## 身份、历史与采用

ontology目录每ID一个当前发现投影；EVOLVE-01版本store/固定commit/基线快照可以保留相同身份的历史字节，但不再计作第二活动本体。逻辑身份含授权library_id，revision相同而digest不同是冲突。旧资料无发布回执可以按REUSE-01固定baseline_snapshot并核验，不臆造历史发布。

候选payload即便写着active也不能凭此变成权威：发布wrapper/回执、来源、适用性与逐主张检查必须成立。当前active/reference/quarantine边界不变；复用优先是用户规定的工作协议，不是外部事实认证。

## 规范用途与仓库交付

normative 表示规定性契约，不自动意味着全局生命周期规则。`asset_role: reusable_work_definition` 或 `composition_pattern` 的节点是用户认可设计的可复用业务契约，只有被具体工作选中且固定才约束该实例；不得覆盖根rule_authorities的工作协议。未标记的历史规范沿原语义按适用性读取，不能凭本文批量宣称领域事实已验证。

本版协议与业务契约以仓库文件维护方式交付，可在ontology中发现；这不等于真实宿主已执行EVOLVE发布、独立Agent审查或生产采用。首次使用可采用可核验的baseline_snapshot，不补造目录generation/用户批准。历史版本放ontology之外的固定store/Git，当前ID仍唯一。业务契约中的场景suite保存期望，不保存某次任务实际通过或私有会话。


## 当前发现投影的一致性

活动INDEX必须与资产的ID、路径、revision、authority和summary一致，不能漏节点或用摘要匹配掩盖内容滞后；`owl_versionIRI`若编码版本，其末段须与revision一致。发布摘要只固定字节，不证明索引语义正确。维护时先验证资产，再生成索引、更新当前模板/字段投影引用，最后生成发布清单；历史fixture、确认、基线和原记录保持不变。新快照不继承旧验证成绩。
