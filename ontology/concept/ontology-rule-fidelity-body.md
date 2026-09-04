---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-fidelity-body
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-rule-fidelity-body/1.0.0
summary: 保真度门禁 — 正文完备性（概念定义/正反例/行数/scaffold）
relations:
  specializes:
    - ontology:concept/ontology-rule
rule_spec:
  body_min_lines: 60
  require_examples: true
  require_concept_definition: true
  codes:
    body_too_short: BODY_TOO_SHORT
    missing_examples: MISSING_EXAMPLES
    missing_concept: MISSING_CONCEPT
    not_scaffoldable: NOT_SCAFFOLDABLE
---

# ontology-rule-fidelity-body

**保真度门禁 — 正文完备性**

- 正文 `<60行` → `[BODY_TOO_SHORT]`（minor，警告；`--strict` 下致命）
- 无 `正例`/`Example` 或无 `反例`/`Counterexample` → `[MISSING_EXAMPLES]`（serious）
- 无概念定义（首段无定义句）→ `[MISSING_CONCEPT]`（fatal，业务域强制）
- 有 `attributes` 但 `ontology_test_scaffold.py` 不可产 → `[NOT_SCAFFOLDABLE]`（minor）

权威来源：`ontology:concept/ontology-fidelity-criterion` 七项清单第1/5/7项。
