---
schema: pdca.asset/v2
id: ontology:domain/skill-wait-wait
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 发现偏差时暂停
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-recovery
  - ontology:concept/pdca-execution-contract
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 发现偏差时暂停

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

遇到目标偏离、权限不清、未知副作用或证据冲突时停止相关动作，记录事实与最小待决问题。暂停不是创建新phase，也不是承诺无宿主支持的后台继续运行。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
