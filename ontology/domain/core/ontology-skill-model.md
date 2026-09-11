---
schema: pdca.asset/v2
id: ontology:domain/core/ontology-skill-model
type: domain
layer: Knowledge
status: active
revision: 3.4.6
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/skill-as-ontology
  - ontology:concept/ontology-evolution
semantic_kind: individual
authority: reference
summary: 技能知识表达的说明文档实例；知识关系不是固定线性层级
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Ontology 与 Skill 的表达关系

本文件是 KnowledgeArtifact 的文档实例，不是一个必须继承的执行流程。

Concept、Domain、Pattern 等 type 是资料分组，不构成 `Ontology → Concept → Pattern → Evidence → Skill` 强制依赖链。类特化、实例、组成和弱关联分别按 [本体关系规范](../../concept/ontology-asset.md) 判断，不将所有知识关系并成执行 DAG。

Skill 知识可描述适用前置、输入、输出、动作与失败处理；一次调用根据当前任务契约选择具体宿主工具。Agent 平台名称不是知识身份，不需要逐平台 adapter；工具是否真的可用仍需实际能力证据。执行权威只来自当前协议与已批准任务，不来自本页。

定义、调用与证据的分工见 [skill-as-ontology](../../concept/skill-as-ontology.md)、[skill-mechanics](../../concept/skill-mechanics.md) 和 [调用契约](../../concept/skill-invocation-contract.md)。
