---
schema: pdca.asset/v2
id: ontology:domain/skill-research
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 来源驱动的领域调研
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/research-first-gate
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-continuous-improvement
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 来源驱动的领域调研

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

明确研究问题、范围和所需来源，优先实际源码、规格与官方资料，核验所用版本。关键主张附可复查来源或实验；推论和未证实假设单独标注。

按读者与任务需要组织报告，复杂关系可用图，不强制图数/URL数量。网络是否必要由时效与契约决定；无能力不假称已检索。报告本身是产物时不设置“先有自身报告”的循环前置。

产出research-report及证据索引；Act按LEARN-01处置知识，允许no_new_knowledge或candidate_only。不额外定义子Agent调度或代替真实用户确认。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
