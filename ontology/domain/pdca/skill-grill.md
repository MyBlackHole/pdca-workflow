---
schema: pdca.asset/v1
id: ontology:domain/skill-grill
name: grill
summary: Interview the user relentlessly about a plan, design, or conclusion.
description: Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-grill/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/grilling-methodology
    - ontology:concept/triage
  testable_signal: "运行 grep -q 'ontology:domain/skill-grill' ontology/domain/pdca/skill-grill.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


---
name: grill
description: Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved.
invocation: manual
---

Run a `$PDCA_HOME/skills/grilling/SKILL.md` session, using `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`.

## 已知坑

- 逐轮追问直至决策树闭合，勿在信息不足时跳过 grill 直接进入方案。
