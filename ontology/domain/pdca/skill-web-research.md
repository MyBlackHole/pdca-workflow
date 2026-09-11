---
schema: pdca.asset/v2
id: ontology:domain/skill-web-research
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 外部来源检索
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:domain/skill-research
  - ontology:concept/capability-protocol
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 外部来源检索

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

契约需要在线资料时使用宿主真实检索工具，核对发布时间与事件时间、版本、来源质量及相关性。保存实际取得的来源，不捏造URL访问、原文或引用。网络不可用时注明影响，不能将离线推测表述为实时查证。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
