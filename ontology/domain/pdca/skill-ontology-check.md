---
schema: pdca.asset/v2
id: ontology:domain/skill-ontology-check
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 本体语义与结构审查
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/ontology-creation-gate
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 本体语义与结构审查

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

执行本体创建门禁的逐项审查，递归定位节点、核对受控字段、关系范围、按类型检查循环、验证属性与来源。结构检查、行为验证和发布授权分开记录。缺源码或宿主运行能力时标not_run，不能靠grep自己的规则宣布通过。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
