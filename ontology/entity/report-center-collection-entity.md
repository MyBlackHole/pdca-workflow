---
schema: pdca.asset/v1
id: ontology:entity/report-center-collection-entity
type: entity
layer: Knowledge
status: active
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
