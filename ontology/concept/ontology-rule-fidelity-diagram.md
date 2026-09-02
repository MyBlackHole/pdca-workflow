---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-fidelity-diagram
type: concept
layer: Knowledge
status: active
summary: 保真度门禁 — 行为可视化与溯源（mermaid/Source行号）
relations:
  specializes:
    - ontology:concept/ontology-rule
rule_spec:
  mermaid_min: 1
  require_source: true
  source_line_pattern: "Source:.*file:line|Source:.*:\\d+"
  codes:
    missing_diagram: MISSING_DIAGRAM
    missing_source: MISSING_SOURCE
---

# ontology-rule-fidelity-diagram

**保真度门禁 — 行为可视化与溯源**

- 无 `mermaid` → `[MISSING_DIAGRAM]`（serious，`concept`/`process`豁免但计分）
- 有 `mermaid` 但无 `Source:` 或 `Source` 不含 `file:line`/`:line` 行号 → `[MISSING_SOURCE]`（minor）

权威来源：`ontology:concept/ontology-fidelity-criterion` 七项清单第4/6项。
