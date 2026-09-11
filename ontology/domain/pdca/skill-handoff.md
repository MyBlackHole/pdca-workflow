---
schema: pdca.asset/v2
id: ontology:domain/skill-handoff
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 持久化交接
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-recovery
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 持久化交接

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

保存任务身份、最后合法阶段、固定基线、产物、证据、待决请求和已知风险。交接仅使用明确持久化输入，不复制活动对话；新独立任务使用新绑定，不冒充原会话。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
