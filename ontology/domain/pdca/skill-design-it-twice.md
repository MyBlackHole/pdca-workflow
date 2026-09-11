---
schema: pdca.asset/v2
id: ontology:domain/skill-design-it-twice
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 比较两种实质不同的设计
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:domain/skill-codebase-design
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 比较两种实质不同的设计

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

在成本合理且契约需要设计权衡时，提出两种真正不同的结构，分别比较复杂度、失败语义、可测试性和迁移风险；选择依据须关联本体约束。只是改名的方案不算独立设计，简单任务不强制双方案。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
