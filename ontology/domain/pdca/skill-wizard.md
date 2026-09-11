---
schema: pdca.asset/v2
id: ontology:domain/skill-wizard
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 分步获取配置输入
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-ai-friendly-confirmation
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 分步获取配置输入

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

仅询问完成当前契约必需的配置，复用已有答案，解释风险和默认值。最终变更应绑定实际配置摘要取得授权；不会因为走完问题清单就自动拥有执行权限。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
