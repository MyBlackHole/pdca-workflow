---
schema: pdca.asset/v2
id: ontology:domain/skill-bug-analysis
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 定位缺陷根因
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:domain/skill-diagnosing-bugs
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 定位缺陷根因

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

描述现象、影响、触发条件、最小复现和反例；用实际证据区分根因与伴随症状。输出可验证根因、修复范围与回归策略。不能仅根据相似历史问题断言当前原因。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
