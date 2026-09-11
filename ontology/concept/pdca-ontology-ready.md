---
schema: pdca.asset/v2
id: ontology:concept/pdca-ontology-ready
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.1.0
summary: 本体基线可用性
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/pdca-execution-contract
---

# 本体基线可用性

进入Do前按CONTEXT-01和CONTRACT-01确认已选本体版本存在、可重读且适用。当前节点可以选择极小知识上下文；建模使用已有元规则验收候选，不能以ontology_exempt跳过用户确认、安全边界或基线。

就绪唯一权威为SCHED-01的scene表：ontology_modeling使用用户目标或已交付父seed，不要求整树已经冻结；ontology_projection必须有TREE-01真实冻结；ontology_conformance_verification需要同一冻结树的固定release与审查输入。所有场景都需要各自NODE/TEST合同、真实能力与授权。不得用modeling例外执行projection，也不得用projection冻结要求阻止根建模。
