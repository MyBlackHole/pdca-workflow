---
schema: pdca.asset/v2
id: ontology:domain/skill-triage
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 确定本体职责和范围
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/flow-plan
  - ontology:concept/pdca-execution-contract
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 3.0.0
---

# 确定本体职责和范围

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

识别目标及三个scene之一，写四字段契约草稿、必须澄清项和范围排除。任务名称或工具名不代替职责。资料充分时直接形成待确认基线，不因输入短而机械追加一轮问题。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
