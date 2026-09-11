---
schema: pdca.asset/v2
id: ontology:pitfall/research-plan-ontology-prompt-gap
type: pitfall
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/research-plan-ontology-prompt-gap/3.1.0
summary: 契约要求调研但Plan期未声明本体计划的pitfall：须在Grill确认锚点与沉淀动作
relations:
  relates_to:
  - ontology:concept/pdca-execution-contract
  - ontology:process/flow-plan
  - ontology:pattern/sm4-storage-encryption
  instance_of:
  - ontology:pitfall
attributes:
- name: plan_no_ontology_prompt
  desc: Plan期契约可能要求调研，却未同步声明本体锚点与沉淀动作
  constraint: required_actions要求基于来源调研时，PRD与契约必须声明目标本体锚点、work_product和Act沉淀动作
  testable_signal: grep -q 'required_actions' ontology/process/flow-plan.md && grep -q '本体锚点' ontology/pitfall/research-plan-ontology-prompt-gap.md
  evidence_level: structure
- name: grill_mandatory_ontology
  desc: Grill必须包含本体产出一问可测
  constraint: 契约要求调研时Grill至少一轮明确本体锚定节点与沉淀计划，captured:true落盘
  testable_signal: grep -q '契约要求调研时Grill' ontology/pitfall/research-plan-ontology-prompt-gap.md
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Plan 期本体计划无提醒 Pitfall

> 来源：`records/T2107-0909-guomi-storage-research/conclusion.md` 偏差记录（T2099 triage 纠正链）。

## 反模式

`execution_contract.required_actions` 已要求基于来源的调研，但 Plan 期未声明本体锚点、
`work_product` 或 Act 沉淀动作，执行者 Grill 又漏问本体，直到 Act 才发现知识无法
落到权威节点，造成报告完成后的返工。

## 正模式（兜底）

1. triage 把调研工具写入 `required_actions` 时同步锚定领域本体节点（有现成 pattern 优先复用）。
2. Grill 必留一轮本体问：锚定哪些节点、本次新增还是修订、Act 校验点是什么。
3. PRD 验收标准单列本体沉淀 AC（结论 `## 本体沉淀` 节 + `disposition.reason` 含 `ontology:` + 反向引用）。
