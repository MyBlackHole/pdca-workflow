---
schema: pdca.asset/v2
id: ontology:concept/ontology-reuse
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-26'
summary: REUSE-01：先找既有定义，再决定复用
---

# REUSE-01：先找既有定义，再决定复用

Plan按目标检索项目／明确允许共享库，逐义务比对版本、证据和适用限制。决定reuse、local_extension、revise或create并给依据；资料命中不等于采用。

复用固定定义与采用记录可以成为modeling产物，不要求复制全库；但必须有实际工作实例、定义引用和适用性检查。未知资料不因被采用就已验证；补证范围进入计划。

只导入具名固定材料，不带入原会话。共享发布是Act单独批准的动作；local_only不等于未做本体，shared_required不允许用候选冒充发布。

## 参考资产的生命周期

本节只治理 `authority: reference` 的知识资产，不改变正式 Task、项目模型或当前 normative 规则的生命周期。
复用现有 `status` 与 `revision` 字段；`active-reference` 是 `authority: reference` + `status: active` 的简称，不是新 schema 或新 status 值。

| 状态 | 含义 | 新任务的处理 |
|---|---|---|
| active-reference | 可检索的参考候选，不代表内容已验证 | 逐主张核对来源、版本与适用性，再按 ADOPT 固定采用 |
| archived | 保留正文供历史比较；因已说明的重复、替代或适用性问题退出一般候选 | 不作为普通新任务的执行依据；历史研究可在获准读域内查阅，重新采用前先审查并获准恢复为新的 active 修订 |
| retired | 保留旧 ID/路径的兼容指针；指针不等于原文 | 不采用指针作为知识定义或运行规则；需要替代对象时单独定位并重新核对，不能静默改写引用 |

新采用时同时核对当前处置说明和拟采用的固定修订，不能换用旧 active 字样绕过归档或退役。

生命周期与验证结论分开。`claim_status: unverified` 不等于错误、重复或无价值；active 不等于 PASS，
归档也不把 unverified 改成 verified。原始来源缺失时明确缺口，不能补造历史正文、测试结果或肯定结论。

## 去重、归档与恢复

AI 直接比较对象语义、独立主张、版本/环境、来源和引用用途，给出保留、修订、归档或退役的理由。
相似标题不证明重复，短定义可能是关系锚点；不按字数、年龄、未引用次数或置信度阈值批量处置。
没有足够证据就保留候选及未知，不为减少文件数删除领域研究或独立证据。

处置必须在获准写域内进行，并增加 revision，在资产正文或现有审查记录说明原因、替代定位和来源缺口。
采用原位归档：保留 ID、路径、原正文、来源和既有验证标记，不搬目录、不自动改写引用。
退役指针没有原文时明确标注缺失，不声称另存了副本。恢复 active 同样需要新的适用性审查与获准修改，
不能只改 status，也不能凭重新检索命中自动恢复。

已采用旧修订的任务继续按 [ADOPT-01](ontology-adoption.md) 核对固定来源；归档本身不迁移任务、
撤销原授权或让旧证据自动过期。发现影响正确性的反证时只停止受影响动作并报告，不因整理知识库全局停工。
这些判断沿用 AI 审查，不新增生命周期 manifest、调度器或项目专用语义 validator。
