---
schema: pdca.asset/v1
id: ontology:concept/pdca-feedback
type: concept
layer: Knowledge
summary: PDCA 执行结果的效果反馈与持续改进输入
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-feedback/1.0.1
relations:
  specializes:
    - ontology:concept/entity
  relates_to:
    - ontology:concept/pdca-verdict
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-continuous-improvement
attributes:
  - name: outcome_feedback
    desc: confirmed 结果的实际效果记录
    constraint: 有遥测则记录可复核效果，无遥测必须显式记录 unknown
    testable_signal: "grep -q 'unknown' ontology/process/pdca-feedback.md && grep -q '效果' ontology/process/pdca-feedback.md"
---
# PDCA 效果反馈

`confirmed` 只表示本轮验收条件满足，不等于长期效果已经证明。Act 必须记录实际效果；没有遥测或后续观察时记录 `unknown`，并把待观察项带入下一轮 Plan。
