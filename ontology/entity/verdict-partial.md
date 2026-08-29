---
schema: pdca.asset/v1
id: ontology:entity/verdict-partial
type: entity
layer: Knowledge
summary: 结论：部分成立（采纳确凿部分，派生跟进）
status: active
relations:
  specializes:
  - ontology:concept/pdca-verdict
---
# verdict-partial

PDCA 阶段结论：任务产出部分成立，仅沉淀确凿可复用部分并派生跟进任务。对应 `meta.verdict.outcome = "partial"`，须经 `pdca-verdict` 子类型锚定。
