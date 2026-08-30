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

## 决策背景（原 ADR-0001：PDCA 工作流架构决策记录机制）
- 背景：flow-plan/do 多处引用 docs/adr/ 作为架构决策记录位置但从未产出实际文件；需明确"什么决策写 ADR"。
- 决策（已退役）：ADR 只记录跨任务/跨周期的架构决策（语言/框架/数据模型/模块边界/集成协议）；单任务决策写入任务内 prd/design；编号 ADR-NNNN；内容含背景/决策/理由/影响。
- 现状：本仓库已确立"本体为唯一决策记录"，ADR 机制退役；跨任务架构决策现由对应 ontology 节点承载（本文件 ontology-asset 即资产层定义）。
