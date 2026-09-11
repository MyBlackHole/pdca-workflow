---
schema: pdca.asset/v2
id: ontology:concept/ontology-fidelity-criterion
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 本体质量：语义可用而非形式计数
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-creation-gate
  - ontology:concept/ontology-rule-attr-testable
---

# 本体质量：语义可用而非形式计数

审查定义、适用/排除、属性、关系、来源、正反例和可执行验证是否支持实际使用。图表在确实帮助解释时提供；正文行数、图数、grep命中和可生成测试骨架不作为默认硬门禁。结构合格不代表行为已验证。

工作节点质量必须落实NODE-01与TEST-01的可运行案例、反例区分力、覆盖矩阵和返工回归，不是每篇写“正例/反例”两个标题。叶与父组合节点都需要测试。
