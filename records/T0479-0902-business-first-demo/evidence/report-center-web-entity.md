---
schema: pdca.asset/v1
id: ontology:entity/report-center-web-entity
type: entity
layer: Knowledge
status: active
summary: ReportCenter Web 子系统实体（ReportCenterSystem 叶）
attributes:
  - name: demo_api
    desc: Demo 报表只读接口桩
    constraint: GET /api/report/demo 返回 {"demo":1}
    testable_signal: "运行 python3 -m pytest tests/test_report_demo.py -v 检查桩接口返回 {demo:1}，且经 scaffold 生成的 tests/test_report_center_web_entity_scaffold.py 通过"
relations:
  specializes:
    - ontology:concept/domain-entity
---

# ReportCenter Web 实体
