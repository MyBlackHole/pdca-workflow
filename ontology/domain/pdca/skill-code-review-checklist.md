---
schema: pdca.asset/v2
id: ontology:domain/skill-code-review-checklist
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 审查覆盖清单
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

# 审查覆盖清单

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

按实际变更选择检查面：输入验证、错误/取消路径、资源所有权、并发与顺序、边界/溢出、兼容性、可观测性和测试。检查不适用项说明理由，不为填满表声称已执行所有验证。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
