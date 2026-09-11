---
schema: pdca.asset/v2
id: ontology:pattern/scientific-research-arc42
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/scientific-research-arc42/3.1.0
summary: 科学调研arc42支：12节全架构文档模板（对齐arc42.org）
relations:
  guides:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:pattern/research-diagram-methodology
  instance_of:
  - ontology:pattern
attributes:
- name: twelve_sections
  desc: 12节
  constraint: 1目标2约束3上下文4方案5构件（C4）6运行时7部署8概念9决策10质量11风险12词汇
  testable_signal: 运行 grep -q 'arc42' ontology/pattern/scientific-research-arc42.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
- name: c4_integration
  desc: C4集成
  constraint: arc42 5构件视图即C4，6运行时即时序
  testable_signal: 检查本文件含 'C4' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/scientific-research-arc42.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 科学调研arc42支

> 来源 `arc42.org` 12节模板（德起源，欧广用）

- **12节**：1目标2约束3上下文4方案5构件(C4)6运行时(时序)7部署8概念9决策(ADR)10质量11风险12词汇 — `arc42` 重于多需，节清单即严肃架构文档自检表
- **与C4组合**：`arc42 5` 即 `C4`，`arc42 6` 即时序，互补不替
