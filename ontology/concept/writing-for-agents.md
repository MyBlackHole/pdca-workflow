---
schema: pdca.asset/v2
id: ontology:concept/writing-for-agents
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/writing-for-agents/3.1.0
summary: 为 Agent 写作：文档和技能的通用写作原则
relations:
  specializes:
  - ontology:principle
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Writing For Agents

为 Agent 写作：文档和技能的通用写作原则。

## Grounding 依赖图

概念必须 grounding 后才能被后续块依赖——读者带来（prerequisite）或先前块引入（introduced）。每 beat 声明 `requires`（读者带来）或 `grounds`（先前块引入）两组概念，候选续写只能从当前 grounded 集合可达。未 grounding 的概念不得被后续块依赖。选择空间被依赖图机械约束。

## 信息层级

信息层级：步骤（in-file step）→ 文件中引用（in-file reference）→ 披露引用（disclosed reference）。
