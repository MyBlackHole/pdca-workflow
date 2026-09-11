---
schema: pdca.boundary-suite/v1
requirements_ref: requirements.md
requirements_digest: ba859a359138079f06e64887ecf1016e27d4e69c33ef379c9872a45f163edde9
cases:
- case_id: P01
  subject_ref: subjects/P01/input.md
  expected_codes:
  - graph_check_missing
  layer: structural_relational
- case_id: P02
  subject_ref: subjects/P02/input.md
  expected_codes:
  - node_binding_missing
  layer: structural_relational
- case_id: P03
  subject_ref: subjects/P03/input.md
  expected_codes:
  - suite_scene_missing
  layer: structural_relational
- case_id: P04
  subject_ref: subjects/P04/input.md
  expected_codes:
  - suite_not_defined
  layer: structural_relational
- case_id: P05
  subject_ref: subjects/P05/input.md
  expected_codes:
  - graph_result
  layer: structural_relational
- case_id: P06
  subject_ref: subjects/P06/input.md
  expected_codes:
  - graph_vertices
  layer: structural_relational
- case_id: P07
  subject_ref: subjects/P07/input.md
  expected_codes:
  - node_identity
  layer: structural_relational
- case_id: P08
  subject_ref: subjects/P08/input.md
  expected_codes:
  - confirmation_identity
  layer: structural_relational
- case_id: P09
  subject_ref: subjects/P09/input.md
  expected_codes:
  - confirmation_edge
  layer: structural_relational
- case_id: P10
  subject_ref: subjects/P10/input.md
  expected_codes:
  - baseline_drift
  layer: structural_relational
- case_id: P11
  subject_ref: subjects/P11/input.md
  expected_codes:
  - budget_quantity
  layer: structural_relational
- case_id: P12
  subject_ref: subjects/P12/input.md
  expected_codes:
  - binding_incomplete
  layer: structural_relational
- case_id: C01
  subject_ref: subjects/C01/input.md
  expected_codes: []
  layer: structural_relational
- case_id: C02
  subject_ref: subjects/C02/input.md
  expected_codes: []
  layer: structural_relational
semantic_cases:
- case_id: P13
  subject_ref: subjects/P13/input.md
  status: NOT_RUN
  reason: requires actual text-capable semantic review; no regex substitution
---

原始上轮补测材料原字节保留。P01-P12与C01-C02精确判定；P13不参加结构pass统计。
