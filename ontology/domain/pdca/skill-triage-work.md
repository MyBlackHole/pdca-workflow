---
schema: pdca.asset/v2
id: ontology:domain/skill-triage-work
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 把需求绑定到场景和目标节点
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/work-scenarios
  - ontology:concept/task-record-identity
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 把需求绑定到场景和目标节点

把已有目标、范围与已知答案写入当前节点Plan；scene取SCENE-01三者之一。新工作先建根seed，已有树按每节点任务覆盖处理，不按临时“独立边界”取消节点。不得虚构能力/确认或提前进入Do。
