---
schema: pdca.asset/v1
id: ontology:concept/pdca-recovery
type: concept
layer: Knowledge
summary: PDCA 失败结果的恢复、升级与重新计划机制
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-recovery/1.0.1
relations:
  specializes:
    - ontology:concept/entity
  relates_to:
    - ontology:concept/pdca-verdict
    - ontology:concept/pdca-task
    - ontology:concept/pdca-continuous-improvement
attributes:
  - name: failure_recovery
    desc: rejected 或 partial 判定的后续处理
    constraint: 必须关联恢复动作、人工升级或后续任务，不能静默结束
    testable_signal: "grep -q 'rejected/partial' ontology/process/pdca-flow-model.md && grep -q '恢复' ontology/process/pdca-recovery.md"
---
# PDCA 失败恢复

`rejected` 或 `partial` 的 Verdict 必须产生可追踪的恢复动作：修正当前任务、升级人工决策，或创建后续 Improvement Task。恢复结果回到下一轮 Plan。
