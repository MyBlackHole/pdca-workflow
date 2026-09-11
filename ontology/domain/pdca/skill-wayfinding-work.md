---
schema: pdca.asset/v2
id: ontology:domain/skill-wayfinding-work
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 从导航到执行输入
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 从导航到执行输入

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

验证找到的材料适用、可读且版本固定，再加入当前任务子图；未实际读取不标已理解，不能把相关链接自动当执行依赖。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
