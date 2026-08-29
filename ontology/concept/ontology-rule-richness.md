---
schema: pdca.asset/v1
id: ontology:concept/ontology-rule-richness
type: concept
layer: Knowledge
summary: AC-5 每 KnowledgeArtifact 实例至少 1 条 guides/relates_to
status: active
relations:
  specializes:
  - ontology:concept/ontology-rule
---
# ontology-rule-richness

**AC-5（关系丰富度）**：每个 KnowledgeArtifact 实例（`pattern`/`principle`/`pitfall`/`fact`/`decision` 类资产）应至少 1 条 `guides` 或 `relates_to`，防止退化为纯分类法（taxonomy）。

- 对应 `ontology-validate.py` 的 AC-5 实现（NO_GUIDES）。
- 注：仅对知识资产类型生效；`concept`/`entity` 等类型豁免（如"类节点"刻意用 concept 以豁免本约束）。
