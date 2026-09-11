---
schema: pdca.asset/v2
id: ontology:domain/skill-grilling
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 逐轮收敛需求
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/grilling-completion
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 逐轮收敛需求

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

本动作是Plan内的需求澄清，不是子任务或附加phase。对每个未决问题记录选项、影响、推荐及真实回答；问题已解决就停止追问，答案变化记录版本。禁止复制推荐答案充当用户确认。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
