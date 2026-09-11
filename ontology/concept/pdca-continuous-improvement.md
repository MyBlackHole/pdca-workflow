---
schema: pdca.asset/v2
id: ontology:concept/pdca-continuous-improvement
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 知识处置、候选与发布
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-creation-gate
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-feedback
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
disposition_values:
- new_knowledge
- revise_knowledge
- confirm_existing
- no_new_knowledge
- reject_hypothesis
- candidate_only
---

# 知识处置、候选与发布

## LEARN-01：强制处置，不强制造知识

每任务Act记录disposition、理由、证据与对象。值保持new_knowledge/revise_knowledge/confirm_existing/no_new_knowledge/reject_hypothesis/candidate_only。已有知识满足时confirm_existing或no_new_knowledge合法；失败可提供反例但不能自证普遍事实。

## 复用、局部细化与共享演进

建模检索和决定由REUSE-01负责。当前参数/特有约束留在NODE或local delta；真正可复用修订按EVOLVE-01候选流程。候选位于records/<task-id>/artifacts/candidates/，wrapper明确candidate，最终payload字节未经发布不能因active字段而成为权威。

发布的内容审查由ontology-creation-gate承担，版本/授权/并发提交由EVOLVE-01唯一规定，跨树采用和显式迁移由ADOPT-01负责。本节点不另定义发布时序或门禁。当前任务不边降低自己的标准边通过；旧树和任务保持固定输入。

本地节点正常完成可先交付并保留candidate_only，不等待共享库发布或其他工作迁移。实质后续修订/审查属于明确工作树节点的新任务及新Agent；目录提交只是宿主事件，不建立隐形无节点业务任务，不让父Agent审批子任务阶段。

所有效果结论须来自真实工作记录；引用数、文件数量、元数据状态或参考模型通过不能证明成功率提高。

## 知识去向不是归档时临时决定

沿用 REUSE-01 的知识义务：existing_reuse 不强制写新 ontology；local_only 说明本地性；shared_required/deferred 保留候选位置、目标库/ID、接续负责人、授权及未完成事项。Act 的 candidate_only 不能取消已确认发布义务，也不能把文件还在 records 写成共享库已更新。

本地任务完整结束不等待所有后代/其他工作；工作索引单独跟踪知识目标。需要实质入库审查、合并或补证时由具名知识维护节点新任务执行，宿主仅提交已审授权字节。禁止整目录搬迁任务日志、确认和测试 actual 到 ontology。
