---
schema: pdca.asset/v1
id: ontology:domain/skill-triage
name: triage
summary: Triage incoming tasks and prioritize based on impact and urgency.
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.
  
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
---

--

Run `$PDCA_HOME/skills/triage-work/SKILL.md`.

## 已知坑

- 查重须搜活跃+归档 task 与 knowledge，事实性 claim 用代码/文档验证而非询问用户。
