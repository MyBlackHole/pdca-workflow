---
name: triage
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.
invocation: manual
relations:
  specializes:
  - ontology:concept/triage
  - ontology:concept/triage-state-machine
  - ontology:concept/agent-ready-brief
  - ontology:concept/ai-disclaimer
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/domain-modeling
  - ontology:concept/task-decomposition
---
name: triage
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.
invocation: manual
---

Run `$PDCA_HOME/skills/triage-work/SKILL.md`.

## 已知坑

- 查重须搜活跃+归档 task 与 knowledge，事实性 claim 用代码/文档验证而非询问用户。
