---
schema: pdca.asset/v2
id: ontology:domain/skill-prototype
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 可丢弃的验证性原型
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-evidence
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 可丢弃的验证性原型

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

原型只验证具名假设，明确非生产范围、输入和退出判据。保存实际观测与无法覆盖的情况；不要将原型可运行直接等同于可生产发布。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
