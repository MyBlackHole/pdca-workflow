---
schema: pdca.asset/v2
id: ontology:domain/skill-grill
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 澄清关键假设
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/pdca-ai-friendly-confirmation
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 澄清关键假设

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

沿目标、边界、风险与验收寻找实质未知；先复用已有回答，再一次提出足以推进的少量问题。意见、推荐与用户答案分离，形成基线后由CONFIRM-01确认，不固定轮数。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
