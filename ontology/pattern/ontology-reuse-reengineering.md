---
schema: pdca.asset/v1
id: ontology:pattern/ontology-reuse-reengineering
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-reuse-reengineering/1.0.0
summary: 本体复用重构（NeOn Scenario4）：重用与重构本体/非本体资源
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
    - ontology:entity/report-center-system
  relates_to:
    - ontology:domain/ontology-hybrid-methodology
    - ontology:pattern/ontology-modular-reference
attributes:
  - name: reuse_scenario4
    desc: NeOn Scenario4 重用重构
    constraint: 重用 `report-center-system` 等存量本体，经重构（改 `composed_of`/`attributes`）产新本体，边可 `graph` 追
    testable_signal: "检查 ontology/pattern/ontology-reuse-reengineering.md 含 'Scenario4' 且 grep -R 'reuse' ontology/ 可命中，且经 validate 通过"
  - name: non_ontological_reuse
    desc: 非本体资源重用
    constraint: 重用 `docs/` `records/` 非本体资源经 `ontology_induction.py` 转本体
    testable_signal: "运行 python3 scripts/ontology_induction.py --help 可调且经 validate 通过"
  - name: reengineering_trace
    desc: 重构可追溯
    constraint: 重构前后 `graph --format dot` 可 `diff`，`disposition` 含来源 `record`
    testable_signal: "检查 records/T04*/conclusion.md 含 'ontology:' 且 graph 可追"
---

# 本体复用重构（NeOn Scenario4）

> 来源 `NeOn Scenario 4` 重用与重构本体/非本体资源

- **重用**：存量 `ontology:entity/report-center-system` 经 `relates_to`/`composed_of` 复用
- **重构**：改 `attributes`/`relations` 产新本体，`graph --format dot` 可 `diff` 追溯
- **非本体转本体**：`docs/` `records/` 经 `ontology_induction.py` 转本体 `pattern`
