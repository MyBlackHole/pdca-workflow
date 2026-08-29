---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-attr-testable
type: concept
layer: Knowledge
summary: AC-4 属性须有可测试信号（attributes[].testable_signal 非空）
status: active
rule_spec:
  attribute_test_field: testable_signal
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-attr-testable

**AC-4（属性可测）**：若 `ontology-asset` 声明了 `attributes`，则每个 `attributes[].testable_signal` 必须非空（描述如何验证该属性，供派生测试）。

- 对应 `ontology-validate.py` 的 AC-4 实现（ATTR_NO_TEST_SIGNAL）。
- 注：仅当资产声明 `attributes` 时触发；不含 `attributes` 的资产不报错（本规则约束"有属性则须可测"，而非"必须有属性"）。
