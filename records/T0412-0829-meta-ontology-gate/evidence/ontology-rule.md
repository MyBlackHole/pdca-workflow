---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule
type: concept
layer: Knowledge
summary: 本体校验规则元概念——ontology-creation-gate 所依据的单条规则的类节点
status: active
relations:
  specializes:
  - ontology:concept/meta-ontology
---
# ontology-rule

本体校验规则元概念：一条"本体创建应满足的约束"。所有具体规则（`ontology-rule-*`）均 `specializes` 本节点。

- **与门禁关系**：规则节点被 `ontology-creation-gate` 通过 `relates_to` 引用，作为门禁的权威依据。
- **实例**：`ontology-rule-type-controlled`(AC-1)、`ontology-rule-non-dangling`(AC-2)、`ontology-rule-acyclic`(AC-3)、`ontology-rule-attr-testable`(AC-4)、`ontology-rule-richness`(AC-5)、`ontology-rule-guides-range`(AC-6)。
