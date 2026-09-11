---
schema: pdca.asset/v2
id: ontology:entity/ontology-deep-integration-tree
type: entity
semantic_kind: class
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 本体组成树与有界节点上下文
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:process/select-task-subgraph
  - ontology:process/work-scenarios
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 本体组成树与有界节点上下文

TREE-01定义唯一父归属的工作目标树；CONTEXT-01只选择当前节点所需知识与固定输入，不能把知识图投影成另一套任意任务结构。每节点各场景完整PDCA见SCENE-01；父节点实现真实组合，不合并孩子任务。
