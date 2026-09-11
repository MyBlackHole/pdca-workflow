---
schema: pdca.asset/v2
id: ontology:domain/ai-efficiency-unified-entrypoint-discipline
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 入口仅做导航
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- knowledge.ai-efficiency.unified-entrypoint-discipline
source_ids:
- T0374-0823-history-review-self-improve
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-feedback
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 入口仅做导航

只有一个根规则索引，入口指向它并根据新建/恢复和当前phase分发。不要在多个入口复制门禁或增加平台分支。
