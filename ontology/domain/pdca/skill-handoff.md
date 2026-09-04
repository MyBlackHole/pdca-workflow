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
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-handoff/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "运行 grep -q 'ontology:domain/skill-handoff' ontology/domain/pdca/skill-handoff.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


--

Run `$PDCA_HOME/skills/handoff-work/SKILL.md`.

## 已知坑

- 压缩对话勿丢关键决策与未竟事项；交接文档须 redact 敏感信息。
