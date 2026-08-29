---
schema: pdca.asset/v1
id: ontology:concept/ontology-asset
type: concept
layer: Knowledge
summary: 本体资产——ontology/ 下的一个节点文件（schema=pdca.asset/v1 + relations 构成的 KG 节点）
status: active
relations:
  specializes:
  - ontology:concept/meta-ontology
  relates_to:
  - ontology:concept/ontology-creation-gate
---
# ontology-asset

本体资产：本工作流中 `ontology/<type>/<slug>.md` 的任意一个节点文件，其 frontmatter（`pdca.asset/v1`）+ `relations` 共同构成知识图谱的一个节点。

- **受约束性**：每个 ontology-asset 在写入/提交前，须经 `ontology-creation-gate` 门禁校验（type 受控词表、frontmatter 必填、引用非空悬、关系无环、`attributes.testable_signal`、知识实例关系丰富度）。
- **与门禁关系**：`ontology-asset` 是 `ontology-creation-gate` 的受检对象（见 `ontology:concept/ontology-creation-gate`）。
