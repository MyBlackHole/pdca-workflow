---
schema: pdca.asset/v1
id: ontology:pattern/ontology-evaluation-oops
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-evaluation-oops/1.0.0
summary: 本体评估OOPS!：41 pitfalls扫描（可验证）与OntoClean一致性评估
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
    - ontology:concept/ontology-validate
  relates_to:
    - ontology:concept/ontology-creation-gate
    - ontology:principle/ontology-governs-ontology
attributes:
  - name: oops_pitfalls
    desc: OOPS! 41 pitfalls扫描
    constraint: 含 P08 missing annotations / P10 missing domain/range / P13 inverse等41项
    testable_signal: "运行 oops扫描（如 python3 scripts/oops_scan.py --ontology-dir ontology）检查0 critical pitfalls 且经 validate 通过"
  - name: ontoclean_consistency
    desc: OntoClean刚性等一致性
    constraint: 评估 `specializes` 刚性一致性，无环且子不违父刚性
    testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查 CYCLE 0 且经 graph islands:0"
  - name: evaluation_gate
    desc: 评估门禁
    constraint: ci-ontology-gate接入OOPS!扫描，critical阻断
    testable_signal: "运行 python3 scripts/ci-ontology-gate.py 返回 GATE OK 且含 oops 检查"
---

# 本体评估 OOPS!（Evaluation）

> 来源 `METHONTOLOGY evaluate` + `OOPS!` 41 pitfalls + `OntoClean`

- **OOPS! 41**：`http://oops.linkeddata.es` 常见坑：P08缺注释、P10缺domain/range、P13 inverse缺、P22命名不一致等，`oops_scan.py` 可顾问式扫描（critical阻断）
- **OntoClean**：`specializes` 刚性/一致性，`validate` `CYCLE`已覆盖
- **门禁**：`ci-ontology-gate` 接入 `oops_scan`，与 `validate` 双 `GATE OK` 硬拦 `islands:0` 外
