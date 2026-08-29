---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-non-dangling
type: concept
layer: Knowledge
summary: AC-2 引用非空悬（relations/domain 中指向的 id 必须存在）
status: active
rule_spec:
  reference_relation_keys:
  - specializes
  - instance_of
  - composed_of
  - configured_by
  - part_of
  - guides
  - relates_to
  extra_reference_fields:
  - domain
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-non-dangling

**AC-2（引用非空悬）**：`relations.*`（`specializes`/`composed_of`/`configured_by`/`guides`/`relates_to` 等）与 `domain` 引用的本体 id，必须在 `ontology/` 中存在对应节点（引用使用本体 id，如 `ontology:concept/foo`）。

- 对应 `ontology-validate.py` 的 AC-2 实现（DANGLING_REF）。
- 违反示例：`specializes: ontology:concept/bar` 但 `bar` 不存在。
