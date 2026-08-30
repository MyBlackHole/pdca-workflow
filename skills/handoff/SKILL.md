---
name: handoff
description: Compact the current conversation into a handoff document so another agent can continue the work.
invocation: manual
relations:
  specializes:
  - ontology:concept/handoff
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/domain-modeling
---
name: handoff
description: Compact the current conversation into a handoff document so another agent (or a future session) can continue the work. Use when wrapping up a session mid-task or passing to another agent.
invocation: manual
---

Run `$PDCA_HOME/skills/handoff-work/SKILL.md`.

## 已知坑

- 压缩对话勿丢关键决策与未竟事项；交接文档须 redact 敏感信息。
