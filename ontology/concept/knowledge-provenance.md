---
schema: pdca.asset/v1
id: ontology:concept/knowledge-provenance
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/knowledge-provenance/1.0.0
summary: Evidence/Experience/Knowledge 分层与来源封存规则（知识仅在 Act 显式投影，须记来源/摘要/理由/连续 revision）
relations:
  specializes:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-continuous-improvement
  - ontology:concept/grounding-dependency
---

# 实验记录与知识投影（knowledge-provenance）

PDCA 产物应分为两层：

- `records/<record-id>/evidence/` 保存内容寻址的原始事实；`experience.md` 保存单次任务的情境化经验。进入 Act 前同时封存两者摘要。
- `ontology/domain/<topic>-<slug>.md` 是跨任务复用、允许演进的知识，不是实验结论的副本。

知识只能在 Act 阶段显式投影。每次投影必须记录来源 record、来源摘要、知识摘要、投影理由和连续 revision。相同内容与理由的重试必须幂等；知识内容或理由变化则形成新 revision。

默认检索优先 knowledge 与 skill。需要解释时通过 manifest 的来源边回到 experience，需要核验时只展开 Evidence 摘要，从而兼顾低噪声检索与可追溯性。

自动阶段流转不得绕过这条边界：Check 必须先形成并封存 record；Act 必须明确知识处置结果后，才能安全归档。

## 来源

- `（原知识层）record-knowledge-provenance.md`
