---
schema: pdca.asset/v2
id: ontology:domain/skill-domain-modeling-work
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 根到叶生成当前节点与子目标
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/work-node-contract
  - ontology:concept/work-ontology-tree
  - ontology:concept/task-test-case
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 根到叶生成当前节点与子目标

依据父seed/用户目标，按NODE-01产出当前节点定义、直接子目标、接口、约束和三场景测试契约。父需求覆盖到孩子或自身组合义务；不一次生成全部后代，不遗漏必需节点。候选按TREE-01冻结，正反例必须具有CASE-01 oracle。
