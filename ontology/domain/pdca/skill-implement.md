---
schema: pdca.asset/v2
id: ontology:domain/skill-implement
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 按已确认契约实现
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/flow-do
  - ontology:concept/pdca-execution-contract
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 按已确认契约实现

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

从执行投影选择依赖已满足的步骤，做范围内修改并运行对应验证。记录真实差异与失败；范围不清或必要能力失效时停止，不自行扩大修改或降低验收。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
