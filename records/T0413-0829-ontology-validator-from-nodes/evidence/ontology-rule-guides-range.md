---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-guides-range
type: concept
layer: Knowledge
summary: AC-6 guides 范围（源须知识类、目标须领域/过程类）
status: active
rule_spec:
  source_types:
  - pattern
  - principle
  - pitfall
  - fact
  - decision
  target_types:
  - domain
  - entity
  - concept
  - process
  - role
  configured_by_target: ontology:entity/tls-configuration
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-guides-range

**AC-6（guides 关系范围）**：`guides` 的 source 必为 KnowledgeArtifact 子类实例，target 必为 DomainEntity / Process 类节点。

- 对应 `ontology-validate.py` 的 AC-6 实现（GUIDES_RANGE）。
- 违反示例：`guides` 指向一个 `concept` 类节点（非领域/过程类）。
