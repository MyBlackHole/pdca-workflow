---
schema: pdca.asset/v2
id: ontology:concept/timeline-integrity-gate
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 事件顺序与真实时间
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-ai-friendly-confirmation
---

# 事件顺序与真实时间

阶段顺序来自TRANSITION-01的回执链。用户确认来源来自CONFIRM-01。时间由实际宿主或工具提供；缺可信时间时保留顺序与unknown，不倒填时间让操作看似获得事前授权。相同时间戳不能证明因果，时间排序不能代替回执。
