---
schema: pdca.asset/v1
id: knowledge:pdca-flow.record-knowledge-provenance
layer: knowledge
summary: Evidence、Experience 与 Knowledge 的分层及来源封存规则
tags: [provenance, knowledge-model, evidence]
scenarios: [software-development]
phases: [check, act]
applies_when: [沉淀任务经验或投影长期知识]
excludes_when: [一次性且无需复用的临时记录]
source_ids: [experience:T0013--07-26-重构实验记录与知识存放模型]
confidence: high
status: active
---
# 实验记录与知识投影

PDCA 产物应分为两层：

- `records/<record-id>/evidence/` 保存内容寻址的原始事实；`experience.md` 保存单次任务的情境化经验。进入 Act 前同时封存两者摘要。
- `knowledge/<topic>/<slug>.md` 是跨任务复用、允许演进的知识。它不是实验结论的副本。

知识只能在 Act 阶段显式投影。每次投影必须记录来源 record、来源摘要、知识摘要、投影理由和连续 revision。相同内容与理由的重试必须幂等；知识内容或理由变化则形成新 revision。

默认检索优先 knowledge 与 skill。需要解释时通过 manifest 的来源边回到 experience，
需要核验时只展开 Evidence 摘要，从而兼顾低噪声检索和可追溯性。

自动阶段流转不得绕过这条边界：Check 必须先形成并封存 record；Act 必须明确知识处置结果后，才能安全归档。
