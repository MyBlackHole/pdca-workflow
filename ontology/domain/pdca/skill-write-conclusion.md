---
schema: pdca.asset/v2
id: ontology:domain/skill-write-conclusion
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 形成验收结论
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-verdict
  - ontology:process/flow-check
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 形成验收结论

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

按VERDICT-01聚合逐项AC结果，说明成立部分、失败、局限和未运行项，保存conclusion.md并固定待确认版本。禁止把生成文档本身当作用户确认或阶段转换。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
