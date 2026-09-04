---
schema: pdca.asset/v1
id: ontology:entity/report-center-collection-entity
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/report-center-collection-entity/1.0.0
summary: ReportCenter Collection 子系统实体（ReportCenterSystem 叶）
attributes:
  - name: demo_collection
    desc: Demo collection 桩
    constraint: GET /api/collection/demo 返回 {"collection":1}
    testable_signal: "运行 python3 -m pytest tests/test_collection_demo.py -v 检查桩返回 {collection:1}，且 scaffold 通过"
relations:
  specializes:
    - ontology:concept/domain-entity
---

# ReportCenter Collection 实体
