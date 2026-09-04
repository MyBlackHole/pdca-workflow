---
schema: pdca.asset/v1
id: ontology:entity/verdict-rejected
type: entity
layer: Knowledge
summary: 结论：驳回（不成立/不采纳）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/verdict-rejected/1.0.0
relations:
  specializes:
  - ontology:concept/pdca-verdict
---
# verdict-rejected

PDCA 阶段结论：任务产出被驳回，结论不成立或不采纳。对应 `meta.verdict.outcome = "rejected"`，须经 `pdca-verdict` 子类型锚定。
