---
schema: pdca.asset/v2
id: ontology:domain/skill-testing-strategy
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 按节点建立详细正反例与返工测试
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/task-unit-test
  - ontology:concept/task-test-case
  - ontology:concept/task-rework
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 按节点建立详细正反例与返工测试

采用TEST-01/CASE-01构造当前场景套件和约束覆盖。正例、非法输入、边界、组合、错误实现变体与历史回归全部有固定输入/oracle/证据；按REWORK-01保存失败、先复现再有限修复、最终同版本全必需回归。文档示例和模型演练不等于实际运行。
