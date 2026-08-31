---
schema: pdca.asset/v1
id: ontology:domain/skill-handoff
name: handoff
summary: Hand off work between phases with proper documentation.
description: Compact the current conversation into a handoff document so another agent can continue the work.
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


--

Run `$PDCA_HOME/skills/handoff-work/SKILL.md`.

## 已知坑

- 压缩对话勿丢关键决策与未竟事项；交接文档须 redact 敏感信息。
