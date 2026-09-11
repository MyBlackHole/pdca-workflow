---
schema: pdca.asset/v2
id: ontology:domain/skill-handoff-work
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 交接包核验
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:domain/skill-handoff
  - ontology:concept/pdca-evidence
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 交接包核验

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

重读交接包的路径、版本和摘要，确认可在授权范围恢复事实；缺失材料列明影响。不因交接者说“已完成”而跳过当前任务验收。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
