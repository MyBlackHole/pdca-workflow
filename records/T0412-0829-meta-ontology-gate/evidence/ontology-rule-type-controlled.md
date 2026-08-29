---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-type-controlled
type: concept
layer: Knowledge
summary: AC-1 type 受控词表且等于父目录名
status: active
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-type-controlled

**AC-1（类型受控）**：`ontology-asset` 的 `type` 必须 ∈ SSOT v3 受控词表（`domain`/`entity`/`concept`/`process`/`role`/`pattern`/`principle`/`pitfall`/`fact`/`decision`，或 README §4 登记的扩展），且 `type` 值 **== 父目录名**（目录即真理）。

- 对应 `ontology-validate.py` 的 AC-1 实现。
- 违反示例：`type: concept` 但文件位于 `pattern/` 下；`type: foo` 不在受控词表。
