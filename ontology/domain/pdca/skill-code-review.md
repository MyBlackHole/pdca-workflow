---
schema: pdca.asset/v2
id: ontology:domain/skill-code-review
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 按正确性与风险审查
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:domain/skill-code-review-checklist
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 按正确性与风险审查

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

确定变更范围与基线，追踪真实调用链，分别检查行为正确性和接口/资源/并发风险。每项发现标位置、触发条件、影响与建议验证；未证实问题标假设。审查不能替代测试，也不能替用户批准。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
