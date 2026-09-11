---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-attr-testable
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 属性约束与可观察验证
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/ontology-rule
  relates_to:
  - ontology:concept/ontology-asset
rule_spec: {}
---

# 属性约束与可观察验证

每项验收性属性必须有非空constraint和testable_signal；信号说明观测对象、判断方法与失败判据。结构检查不能替代行为测试。对实际代码不存在的测试不填通过，而是明确未执行或生成待运行测试设计。
