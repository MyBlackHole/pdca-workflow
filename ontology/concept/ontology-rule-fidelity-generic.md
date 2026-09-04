---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-fidelity-generic
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-rule-fidelity-generic/1.0.0
summary: 保真度门禁 — 拒绝泛化signal（零容忍），attributes须含可执行动词
relations:
  specializes:
    - ontology:concept/ontology-rule
rule_spec:
  generic_phrases:
    - "检查本文件"
    - "相关章节的完整性"
    - "相关章节的定义完整性"
    - "检查本文件内容完整性"
    - "检查本文件核心相关章节"
  required_verbs:
    - "grep -q"
    - "grep -c"
    - "python3 scripts/"
    - "gate.py"
    - "scaffold"
    - "pytest"
  code: ATTR_GENERIC
---

# ontology-rule-fidelity-generic

**保真度门禁 — 零容忍泛化signal（Q3确认）**

若 `attributes[].testable_signal` 含 `generic_phrases` 任一短语，或不含 `required_verbs` 任一可执行动词，则判 `[ATTR_GENERIC]` 致命，直接阻断。

- 对应 `ontology-validate.py` 的 fidelity 检查（`--check fidelity` 或默认增量）。
- 存量豁免由 `audit-report.md` 豁免清单承载，限期清零；增量提交零容忍。
- 权威来源：`ontology:concept/ontology-fidelity-criterion` 的七项清单第2项。
