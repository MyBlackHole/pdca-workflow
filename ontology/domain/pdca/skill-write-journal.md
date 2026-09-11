---
schema: pdca.asset/v2
id: ontology:domain/skill-write-journal
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 记录工作事实
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:concept/task-record-identity
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 记录工作事实

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

在当前任务记录实际动作、结果、偏差和来源；已有证据用ID引用，不复制大量工具日志到核心上下文。时间来自真实工具，没有则明确未知；日志不能替代转换回执、授权或验收证据。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
