---
schema: pdca.asset/v2
id: ontology:domain/skill-advance-phase
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 阶段推进动作
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-gate
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 阶段推进动作

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

只执行TRANSITION-01：重读当前事实、核验对应GATE-01、写单阶段回执、重读后更新task快照。重复请求返回匹配回执；未满足条件保持原phase并报告缺项。不要调用旧CLI或把目标状态存在当作提交成功。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
