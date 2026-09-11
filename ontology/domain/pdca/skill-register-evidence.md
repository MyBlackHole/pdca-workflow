---
schema: pdca.asset/v2
id: ontology:domain/skill-register-evidence
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 登记可复核证据
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-evidence
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 登记可复核证据

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

读取真实产物/输出，核对授权路径和来源，使用真实摘要工具，写evidence.md条目并关联AC。依据EVIDENCE-01选择类型，更正使用新版本。只有工具实际运行才登记运行结果；没有输出则记录未执行或未知，不填pass。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
