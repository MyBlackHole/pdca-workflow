---
schema: pdca.asset/v2
id: ontology:domain/skill-to-tickets
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 逐目标节点建立完整任务
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:process/work-scenarios
  - ontology:concept/work-tree-scheduling
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 逐目标节点建立完整任务

TREE-01/SCENE-01要求每个目标节点每场景一个完整PDCA任务，根和组合节点不能省略。按SCHED-01生成任务清单/直接依赖/写域/真实宿主绑定。单条约束或工具调用是节点内步骤，不能用知识引用数替代目标节点数；不合并实际目标节点，不由父Agent持续控制。
